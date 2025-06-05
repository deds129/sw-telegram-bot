from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class UserBase(BaseModel):
    id: int

class UserCreate(UserBase):
    pass

class User(UserBase):
    created_at: datetime

    class Config:
        from_attributes = True

class HabitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class HabitCreate(HabitBase):
    pass

class Habit(HabitBase):
    id: UUID
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PeriodBase(BaseModel):
    habit_id: UUID

class PeriodCreate(PeriodBase):
    pass

class Period(PeriodBase):
    id: UUID
    start_at: datetime
    end_at: datetime | None

    class Config:
        from_attributes = True

class RelapseBase(BaseModel):
    period_id: UUID
    reason: str | None = Field(None, max_length=500)

class RelapseCreate(RelapseBase):
    pass

class Relapse(RelapseBase):
    id: UUID
    occurred_at: datetime

    class Config:
        from_attributes = True

class TimeProgress(BaseModel):
    days: int
    hours: int
    minutes: int
    seconds: int

class HabitStats(BaseModel):
    total_relapses: int
    average_period: TimeProgress
    current_streak: TimeProgress 