import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from app.src.services.db.base import session_factory
from app.src.services.db.dao.settings_dao import SettingDao
from app.src.services.db.models import SettingKeys

logger = logging.getLogger(__name__)


async def check_subscribe_on_channel(
    channel_id: str | int, user_id: int, bot: Bot
) -> bool:
    """Проверяет подписку на калан"""
    chat_member = await bot.get_chat_member(channel_id, user_id)
    if chat_member.status in (ChatMemberStatus.KICKED, ChatMemberStatus.LEFT):
        logger.debug(chat_member)
        return False
    return True


async def get_channel_id() -> str | None:
    """Проверяет включена ли проверка подписки на канал, если включена, то возвращает
    id канала"""
    async with session_factory() as session:
        settings_dao = SettingDao(session)
        is_enable = await settings_dao.find_one(key=SettingKeys.CHECK_IS_ENABLE)
        if is_enable.value != "enable":
            return
        channel = await settings_dao.find_one_or_none(key=SettingKeys.CHANNEL)
        if channel is not None:
            return channel.value
