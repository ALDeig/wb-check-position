import asyncio
from collections.abc import Sequence
from pathlib import Path

from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramNotFound,
    TelegramUnauthorizedError,
)
from aiogram.types import Message

from app.src.services.db.base import session_factory
from app.src.services.db.dao.settings_dao import SettingDao
from app.src.services.db.dao.user_dao import UserDao
from app.src.services.db.models import MUser, SettingKeys


async def mailing_to_users(msg: Message) -> asyncio.Task:
    async with session_factory() as session:
        users = await UserDao(session).find_all()
    return asyncio.create_task(_mailing(msg, users), name="mailing")


async def get_file_with_users() -> Path:
    text = f"{'№':<3} | {'Имя':<30} | {'Юзернейм':<20} | Источник\n{'-':-<70}\n"
    async with session_factory() as session:
        users = await UserDao(session).find_all()
    for cnt, user in enumerate(users, start=1):
        line = (
            f"{cnt:<3} | {user.fullname or "":<30} | "
            f"{user.username or "":<20} | {user.source or ""}\n"
        )
        text += line
    file = Path("users.txt")
    file.write_text(text)
    return file


async def change_state_check_subscribe(state: str) -> str:
    async with session_factory() as session:
        await SettingDao(session).update(
            {"value": state}, key=SettingKeys.CHECK_IS_ENABLE
        )
    text = "Проверка отключена!" if state == "disable" else "Проверка включена!"
    return text


async def set_channel_for_check_subscribe(channel: str):
    async with session_factory() as session:
        await SettingDao(session).insert_or_update(
            {"key": SettingKeys.CHANNEL, "value": channel}
        )


async def set_start_message(text: str):
    async with session_factory() as session:
        await SettingDao(session).insert_or_update(
            {"key": SettingKeys.START_MESSAGE, "value": text}
        )


async def set_help_message(text: str):
    async with session_factory() as session:
        await SettingDao(session).insert_or_update(
            {"key": SettingKeys.HELP_MESSAGE, "value": text}
        )


async def _mailing(msg: Message, users: Sequence[MUser]) -> None:
    for user in users:
        try:
            await msg.copy_to(user.id)
        except (TelegramForbiddenError, TelegramUnauthorizedError, TelegramNotFound):
            async with session_factory() as session:
                await UserDao(session).delete(id=user.id)
