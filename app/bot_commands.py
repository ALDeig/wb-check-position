from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_commands(bot: Bot):
    await bot.set_my_commands(
        commands=[BotCommand(command="start", description="Перезапустить бот")],
        scope=BotCommandScopeAllPrivateChats(),
    )


