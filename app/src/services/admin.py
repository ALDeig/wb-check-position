import asyncio
from pathlib import Path
from typing import Sequence

from aiogram import Bot

from app.src.services.db.base import session_factory
from app.src.services.db.dao.settings_dao import SettingDao
from app.src.services.db.dao.user_dao import UserDao
from app.src.services.db.models import MUser, SettingKeys




async def mailing_to_users(text: str, bot: Bot):
    async with session_factory() as session:
        users = await UserDao(session).find_all()
    asyncio.create_task(_mailing(text, users, bot), name="mailing")


async def get_file_with_users() -> Path:
    text = f"{'Имя':<20} | {'Юзернейм':<20} | Источник\n{'-':-<60}\n"
    async with session_factory() as session:
        users = await UserDao(session).find_all()
    for user in users:
        line = f"{user.fullname:<20} | {user.username:<20} | {user.source}\n"
        text += line
    file = Path("users.txt")
    file.write_text(text)
    return file


async def change_state_check_subscribe(state: str):
    async with session_factory() as session:
        await SettingDao(session).update(
            {"value": state}, key=SettingKeys.CHECK_IS_ENABLE
        )


async def set_start_message(text: str):
    async with session_factory() as session:
        await SettingDao(session).insert_or_update(
            {"key": SettingKeys.START_MESSAGE, "value": text}
        )


async def _mailing(text: str, users: Sequence[MUser], bot: Bot):
    for user in users:
        await bot.send_message(user.id, text)
