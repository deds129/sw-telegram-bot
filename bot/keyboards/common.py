from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="➕ Add Habit"), KeyboardButton(text="📊 My Habits")],
        [KeyboardButton(text="📝 Log Relapse"), KeyboardButton(text="📈 Progress")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_habit_list_keyboard(habits: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for habit in habits:
        builder.button(text=habit.name, callback_data=f"habit:{habit.id}")
    builder.adjust(1)
    return builder.as_markup()

def get_habit_actions_keyboard(habit_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 View Stats", callback_data=f"stats:{habit_id}")
    builder.button(text="📝 Log Relapse", callback_data=f"relapse:{habit_id}")
    builder.button(text="❌ Delete", callback_data=f"delete:{habit_id}")
    builder.adjust(2, 1)
    return builder.as_markup()

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Yes", callback_data="confirm")
    builder.button(text="❌ No", callback_data="cancel")
    return builder.as_markup() 