from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_change_state_check_subscribe() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Включить подписку", callback_data="enable")],
        [InlineKeyboardButton(text="Выключить подписку", callback_data="disable")],
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
