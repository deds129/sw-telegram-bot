from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.base import get_async_session
from bot.fsm.habit import RelapseLogging
from bot.services.habit import HabitService
from bot.keyboards.common import get_habit_list_keyboard, get_habit_actions_keyboard

router = Router()

@router.message(F.text == "📊 My Habits")
async def show_habits(
    message: Message,
    session: AsyncSession
):
    habit_service = HabitService(session)
    habits = await habit_service.get_user_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "У вас пока нет привычек!\n"
            "Нажмите кнопку ➕ Add Habit, чтобы создать первую."
        )
        return

    await message.answer(
        "Ваши активные привычки:\n"
        "Выберите одну для просмотра деталей:",
        reply_markup=get_habit_list_keyboard(habits)
    )

@router.callback_query(F.data.startswith("habit:"))
@router.callback_query(F.data.startswith("stats:"))
async def show_habit_details(
    callback: CallbackQuery,
    session: AsyncSession
):
    habit_id = callback.data.split(":")[1]
    habit_service = HabitService(session)
    stats = await habit_service.get_habit_stats(habit_id)
    
    streak = stats.current_streak
    streak_text = f"{streak.days}д {streak.hours}ч {streak.minutes}м {streak.seconds}с"
    
    avg_period = stats.average_period
    avg_period_text = f"{avg_period.days}д {avg_period.hours}ч {avg_period.minutes}м {avg_period.seconds}с"
    
    await callback.message.edit_text(
        f"📊 Статистика:\n\n"
        f"Текущая серия: {streak_text}\n"
        f"Всего срывов: {stats.total_relapses}\n"
        f"Средняя продолжительность: {avg_period_text}\n\n"
        f"Что бы вы хотели сделать?",
        reply_markup=get_habit_actions_keyboard(habit_id)
    )

@router.message(F.text == "📝 Log Relapse")
async def start_relapse_logging(
    message: Message,
    state: FSMContext,
    session: AsyncSession
):
    habit_service = HabitService(session)
    habits = await habit_service.get_user_habits(message.from_user.id)
    
    if not habits:
        await message.answer("У вас нет привычек для отметки срыва!")
        return

    await message.answer(
        "Выберите привычку, по которой произошел срыв:",
        reply_markup=get_habit_list_keyboard(habits)
    )
    await state.set_state(RelapseLogging.waiting_for_habit)

@router.callback_query(F.data.startswith("relapse:"))
async def start_relapse_from_habit(callback: CallbackQuery, state: FSMContext):
    habit_id = callback.data.split(":")[1]
    await state.update_data(habit_id=habit_id)
    
    await callback.message.edit_text(
        "Хотите добавить причину срыва? (необязательно)\n"
        "Это поможет выявить триггеры.\n\n"
        "Напишите причину или отправьте /skip чтобы пропустить."
    )
    await state.set_state(RelapseLogging.waiting_for_reason)

@router.callback_query(RelapseLogging.waiting_for_habit)
async def process_relapse_habit(callback: CallbackQuery, state: FSMContext):
    habit_id = callback.data.split(":")[1]
    await state.update_data(habit_id=habit_id)
    
    await callback.message.edit_text(
        "Хотите добавить причину срыва? (необязательно)\n"
        "Это поможет выявить триггеры.\n\n"
        "Напишите причину или отправьте /skip чтобы пропустить."
    )
    await state.set_state(RelapseLogging.waiting_for_reason)

@router.message(RelapseLogging.waiting_for_reason)
async def process_relapse_reason(
    message: Message,
    state: FSMContext,
    session: AsyncSession
):
    data = await state.get_data()
    habit_id = data["habit_id"]
    reason = None if message.text == "/skip" else message.text
    
    habit_service = HabitService(session)
    await habit_service.log_relapse(habit_id, reason)
    
    await message.answer(
        "Срыв отмечен. Не расстраивайтесь, каждая неудача - это шаг к успеху! 💪\n"
        "Ваша новая серия начинается прямо сейчас."
    )
    await state.clear() 