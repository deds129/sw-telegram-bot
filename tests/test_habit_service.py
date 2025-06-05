import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.db.base import Base
from bot.db.models import User, Habit, Period, Relapse
from bot.services.habit import HabitService
from bot.models.schemas import HabitCreate

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def session(engine):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
def user_id():
    return 12345

@pytest.mark.asyncio
async def test_create_habit(session, user_id):
    service = HabitService(session)
    habit_data = HabitCreate(name="Test Habit")
    
    habit = await service.create_habit(user_id, habit_data)
    
    assert habit.name == "Test Habit"
    assert habit.user_id == user_id
    assert habit.is_active == True
    
    # Check that a period was created
    result = await session.execute(
        "SELECT COUNT(*) FROM periods WHERE habit_id = :habit_id",
        {"habit_id": habit.id}
    )
    period_count = result.scalar()
    assert period_count == 1

@pytest.mark.asyncio
async def test_get_user_habits(session, user_id):
    service = HabitService(session)
    
    # Create test habits
    habit1 = await service.create_habit(user_id, HabitCreate(name="Habit 1"))
    habit2 = await service.create_habit(user_id, HabitCreate(name="Habit 2"))
    
    habits = await service.get_user_habits(user_id)
    assert len(habits) == 2
    assert {h.name for h in habits} == {"Habit 1", "Habit 2"}

@pytest.mark.asyncio
async def test_habit_limit(session, user_id):
    service = HabitService(session)
    
    # Create 3 habits (maximum)
    for i in range(3):
        await service.create_habit(user_id, HabitCreate(name=f"Habit {i+1}"))
    
    # Try to create a 4th habit
    with pytest.raises(ValueError) as exc_info:
        await service.create_habit(user_id, HabitCreate(name="Habit 4"))
    assert "Maximum number of active habits reached" in str(exc_info.value)

@pytest.mark.asyncio
async def test_log_relapse(session, user_id):
    service = HabitService(session)
    
    # Create a habit and get its initial period
    habit = await service.create_habit(user_id, HabitCreate(name="Test Habit"))
    
    # Log a relapse
    relapse = await service.log_relapse(str(habit.id), "Test reason")
    
    # Verify the relapse was logged
    assert relapse.reason == "Test reason"
    
    # Verify a new period was created
    result = await session.execute(
        "SELECT COUNT(*) FROM periods WHERE habit_id = :habit_id",
        {"habit_id": habit.id}
    )
    period_count = result.scalar()
    assert period_count == 2  # Initial period + new period after relapse 