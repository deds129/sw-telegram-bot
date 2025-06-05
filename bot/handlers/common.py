from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards.common import get_main_keyboard, get_habit_list_keyboard
from bot.fsm.habit import HabitCreation
from bot.services.habit import HabitService


# Создаем корневой роутер для всего модуля
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в Strong Will Bot! 🦾\n\n"
        "Я помогу вам отслеживать ваши привычки и оставаться на правильном пути.\n\n"
        "Вы можете:\n"
        "➕ Добавить до 3 привычек для отслеживания\n"
        "📊 Просматривать свой прогресс\n"
        "📝 Отмечать срывы\n"
        "📈 Смотреть статистику\n\n"
        "Используйте кнопки меню ниже для навигации!",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🔍 Here's what you can do:\n\n"
        "Commands:\n"
        "/start - Show main menu\n"
        "/habit_add - Create new habit\n"
        "/habits - List your habits\n"
        "/relapse - Log a relapse\n"
        "/history - View history\n\n"
        "Or use the buttons below 👇",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("habit_add"))
@router.message(F.text == "➕ Add Habit")
async def start_new_habit(message: Message, state: FSMContext):
    await message.answer(
        "Какую привычку вы хотите отслеживать? 🤔\n\n"
        "Примеры:\n"
        "- Не курить 🚭\n"
        "- Ежедневные упражнения 🏃‍♂️\n"
        "- Медитация 🧘‍♂️\n"
        "- Здоровое питание 🥗\n\n"
        "Введите название привычки:"
    )
    await state.set_state(HabitCreation.waiting_for_name)

@router.message(F.text == "📈 Progress")
async def show_progress(message: Message, session: AsyncSession):
    habit_service = HabitService(session)
    habits = await habit_service.get_user_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "У вас пока нет привычек для отслеживания!\n"
            "Нажмите кнопку ➕ Add Habit, чтобы начать."
        )
        return

    await message.answer(
        "Выберите привычку для просмотра прогресса:",
        reply_markup=get_habit_list_keyboard(habits)
    )
