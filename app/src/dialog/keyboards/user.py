from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def user_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Мои артикулы", callback_data="articules"),
        InlineKeyboardButton(
            text="Польза для селлеров", url="https://t.me/+p2MUyk-7SvU4MTgy"
        ),
        InlineKeyboardButton(
            text="Бот для отслеживания заказов",
            url="https://t.me/WBoosterBot?start=bot_pozicii",
        ),
        InlineKeyboardButton(text="Инструкция", callback_data="docs"),
    )
    builder.adjust(2)
    return builder.as_markup()
