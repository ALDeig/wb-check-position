import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
)

logger = logging.getLogger(__name__)

ADMIN_COMMANS = [
    BotCommand(command="start", description="Перезапустить бот"),
    BotCommand(command="mailing", description="Рассылка пользователям"),
    BotCommand(command="users", description="Список пользователей"),
    BotCommand(command="channel_check", description="Проверка подписки"),
    BotCommand(command="set_channel", description="ID канала для проверки"),
    BotCommand(
        command="set_start_text", description="Установить приветственное сообщение"
    ),
    BotCommand(command="set_help_text", description="Установить текст инструкции"),
]


async def set_commands(bot: Bot, admins: list[int]):
    await bot.set_my_commands(
        commands=[BotCommand(command="start", description="Перезапустить бот")],
        scope=BotCommandScopeAllPrivateChats(),
    )
    for admin in admins:
        try:
            await bot.set_my_commands(
                ADMIN_COMMANS, scope=BotCommandScopeChat(chat_id=admin)
            )
        except TelegramBadRequest as er:
            logger.error(f"Set command error {admin}: {er.message}")
