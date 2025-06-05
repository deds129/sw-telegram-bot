from aiogram.fsm.state import StatesGroup, State

class HabitCreation(StatesGroup):
    waiting_for_name = State()

class RelapseLogging(StatesGroup):
    waiting_for_habit = State()
    waiting_for_reason = State()

class HabitDeletion(StatesGroup):
    waiting_for_confirmation = State()
