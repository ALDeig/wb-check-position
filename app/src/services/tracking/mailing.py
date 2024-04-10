from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNotFound,
    TelegramUnauthorizedError,
)

from app.src.services.db.base import session_factory
from app.src.services.db.dao.track_dao import NoticeDao, QueryDao, TrackDao
from app.src.services.db.models import MNotice
from app.src.services.exceptions import SendError


async def save_notices(notices: list[MNotice]):
    async with session_factory() as session:
        await NoticeDao(session).add_all(notices)


async def mailing_notices(bot: Bot):
    async with session_factory() as session:
        notices = await NoticeDao(session).find_all()
    for notice in notices:
        try:
            await _send_notice(bot, notice)
        except SendError:
            if notice.track_id:
                await _remove_track(notice.track_id)


async def _send_notice(bot: Bot, notice: MNotice):
    try:
        await bot.send_message(notice.user_id, notice.text)
    except (
        TelegramNotFound,
        TelegramBadRequest,
        TelegramForbiddenError,
        TelegramUnauthorizedError,
    ):
        raise SendError


async def _remove_track(track_id: int) -> None:
    async with session_factory() as session:
        track_dao = TrackDao(session)
        track = await track_dao.find_one(id=track_id)
        await track_dao.delete(id=track_id)
        if not await track_dao.count(query_id=track.query_id):
            await QueryDao(session).delete(id=track.query_id)
