from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_after_query(track_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Обновить", callback_data=f"update:{track_id}")],
        [InlineKeyboardButton(text="Отслеживать", callback_data=f"add:{track_id}")],
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb


def remove_track(track_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="Не отслеживать", callback_data=f"remove:{track_id}"
            )
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
