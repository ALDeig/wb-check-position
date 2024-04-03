import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot_commands import set_commands
from app.settings import settings
from app.src.services.schedule import scheduler, add_jobs
from app.src.dialog.handlers import admin 
from app.src.dialog.handlers import user
from app.src.dialog.handlers import tracking

logger = logging.getLogger(__name__)


def include_routers(dp: Dispatcher):
    dp.include_routers(admin.router, user.router, tracking.router)


def include_filters(dp: Dispatcher):
    dp.message.filter(F.chat.type == "private")
    # dp.callback_query.filter(F.chat.type == "private")


async def main():
    bot = Bot(
        token=settings.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    include_filters(dp)
    include_routers(dp)

    await set_commands(bot, settings.ADMINS)

    bot_info = await bot.get_me()
    logger.info(
        f"Starting bot!!! UserName: @{bot_info.username} FullName: {bot_info.full_name}"
    )
    add_jobs(bot)
    
    try:
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    try:
        logger.info("Bot starting...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.error("Bot stopped...")
