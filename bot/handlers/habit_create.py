from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.base import get_async_session
from bot.fsm.habit import HabitCreation, HabitDeletion
from bot.services.habit import HabitService
from bot.models.schemas import HabitCreate
from bot.keyboards.common import get_habit_actions_keyboard, get_confirm_keyboard

# Создаем корневой роутер для всего модуля
router = Router()
user_data = {}  # Временное хранилище данных в памяти

@router.message(HabitCreation.waiting_for_name)
async def process_habit_name(
    message: Message,
    state: FSMContext,
    session: AsyncSession
):
    habit_service = HabitService(session)
    try:
        habit = await habit_service.create_habit(
            user_id=message.from_user.id,
            habit_data=HabitCreate(name=message.text)
        )
        await message.answer(
            f"✅ Привычка '{habit.name}' создана!\n\n"
            f"Я помогу вам отслеживать её. Вы можете:\n"
            f"📊 Просматривать статистику\n"
            f"📝 Отмечать срывы\n"
            f"❌ Удалить привычку",
            reply_markup=get_habit_actions_keyboard(str(habit.id))
        )
    except ValueError as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()

@router.callback_query(F.data.startswith("delete:"))
async def process_delete_request(callback: CallbackQuery, state: FSMContext):
    habit_id = callback.data.split(":")[1]
    await state.update_data(habit_id=habit_id)
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить эту привычку?\n"
        "Весь прогресс будет потерян!",
        reply_markup=get_confirm_keyboard()
    )
    await state.set_state(HabitDeletion.waiting_for_confirmation)

@router.callback_query(HabitDeletion.waiting_for_confirmation, F.data == "confirm")
async def confirm_habit_deletion(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
):
    data = await state.get_data()
    habit_id = data["habit_id"]
    
    habit_service = HabitService(session)
    try:
        await habit_service.delete_habit(habit_id)
        await callback.message.edit_text("✅ Привычка успешно удалена!")
    except ValueError as e:
        await callback.message.edit_text(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()

@router.callback_query(HabitDeletion.waiting_for_confirmation, F.data == "cancel")
async def cancel_habit_deletion(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Удаление отменено.")
    await state.clear()
