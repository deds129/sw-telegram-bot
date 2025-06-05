from datetime import datetime
import pytz
from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from bot.db.models import User, Habit, Period, Relapse
from bot.models.schemas import HabitCreate, HabitStats, TimeProgress

class HabitService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_habits(self, user_id: int) -> List[Habit]:
        result = await self.session.execute(
            select(Habit).where(Habit.user_id == user_id, Habit.is_active == True)
        )
        return list(result.scalars().all())

    async def create_habit(self, user_id: int, habit_data: HabitCreate) -> Habit:
        # Check if user exists, create if not
        user = await self.session.get(User, user_id)
        if not user:
            user = User(id=user_id)
            self.session.add(user)

        # Check habit limit
        habits_count = await self.session.scalar(
            select(func.count()).where(
                Habit.user_id == user_id,
                Habit.is_active == True
            )
        )
        if habits_count >= 3:
            raise ValueError("Maximum number of active habits reached (3)")

        # Create habit
        habit = Habit(user_id=user_id, name=habit_data.name)
        self.session.add(habit)
        await self.session.flush()

        # Create initial period
        period = Period(habit_id=habit.id)
        self.session.add(period)
        await self.session.commit()

        return habit

    async def delete_habit(self, habit_id: str) -> None:
        # Get the habit
        habit = await self.session.get(Habit, habit_id)
        if not habit:
            raise ValueError("Habit not found")

        # Soft delete by marking as inactive
        habit.is_active = False
        await self.session.commit()

    async def log_relapse(self, habit_id: str, reason: str | None = None) -> Relapse:
        # Get current period
        result = await self.session.execute(
            select(Period)
            .where(Period.habit_id == habit_id, Period.end_at.is_(None))
        )
        current_period = result.scalar_one_or_none()
        if not current_period:
            raise ValueError("No active period found for this habit")

        now = datetime.now(pytz.UTC)

        # End current period
        current_period.end_at = now

        # Create relapse
        relapse = Relapse(period_id=current_period.id, reason=reason)
        self.session.add(relapse)

        # Start new period
        new_period = Period(habit_id=habit_id, start_at=now)
        self.session.add(new_period)

        await self.session.commit()
        return relapse

    def _seconds_to_time_progress(self, total_seconds: int) -> TimeProgress:
        days = total_seconds // (24 * 3600)
        remaining = total_seconds % (24 * 3600)
        
        hours = remaining // 3600
        remaining = remaining % 3600
        
        minutes = remaining // 60
        seconds = remaining % 60
        
        return TimeProgress(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )

    def _calculate_time_progress(self, start_time: datetime) -> TimeProgress:
        now = datetime.now(pytz.UTC)
        if not start_time.tzinfo:
            start_time = pytz.UTC.localize(start_time)
        
        total_seconds = int((now - start_time).total_seconds())
        return self._seconds_to_time_progress(total_seconds)

    async def get_habit_stats(self, habit_id: str) -> HabitStats:
        # Get all periods
        result = await self.session.execute(
            select(Period).where(Period.habit_id == habit_id)
        )
        periods = result.scalars().all()

        # Calculate stats
        completed_periods = [p for p in periods if p.end_at is not None]
        total_relapses = len(completed_periods)  # Remove the -1 adjustment
        
        # Calculate average period length
        total_seconds = 0
        for period in completed_periods:
            if not period.start_at.tzinfo:
                period.start_at = pytz.UTC.localize(period.start_at)
            if not period.end_at.tzinfo:
                period.end_at = pytz.UTC.localize(period.end_at)
            duration = period.end_at - period.start_at
            total_seconds += int(duration.total_seconds())

        avg_period_seconds = total_seconds // len(completed_periods) if completed_periods else 0
        avg_period_progress = self._seconds_to_time_progress(avg_period_seconds)

        # Calculate current streak
        current_period = next((p for p in periods if p.end_at is None), None)
        current_streak = TimeProgress(days=0, hours=0, minutes=0, seconds=0)
        if current_period:
            current_streak = self._calculate_time_progress(current_period.start_at)

        return HabitStats(
            total_relapses=total_relapses,
            average_period=avg_period_progress,
            current_streak=current_streak
        ) 