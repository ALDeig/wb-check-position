import logging
from typing import Sequence

from aiogram import Bot

from app.src.services.channel import check_subscribe_on_channel, get_channel_id
from app.src.services.db.base import session_factory
from app.src.services.db.dao.track_dao import NoticeDao, QueryDao, TrackDao
from app.src.services.db.models import MNotice, MQuery, MTrack
from app.src.services.texts.tracking import get_tracking_text
from app.src.services.texts.user import UNSUBSCRIBE
from app.src.services.tracking.mailing import save_notices
from app.src.services.wb.parser import Parser, Positions


logger = logging.getLogger(__name__)


class Tracking:
    """Сервис работы с треками. Обновление позиций, создание треков."""

    @classmethod
    async def update_tracks_position(cls, channel_id: str | None, bot: Bot):
        verified_users = dict()
        await cls._clear_notices()
        queries = await cls.get_all_tracks(notice_enabled=True)
        for query in queries:
            notices = []
            tracks = {
                track.articule: track for track in query.tracks if track.notice_enabled
            }
            logger.info(tracks)
            if channel_id:
                tracks = await cls._exclude_unsubscribed_users(
                    verified_users, channel_id, tracks, bot
                )
                logger.info(tracks)
                if not tracks:
                    continue
            parser = Parser(articules=list(tracks.keys()), query=query.query)
            positions = await parser.get_positions()
            for articule, track in tracks.items():
                text = get_tracking_text(query.query, articule, positions[articule])
                notices.append(
                    MNotice(user_id=track.user_id, track_id=track.id, text=text)
                )
            await save_notices(notices)
        notices = []
        for user_id, is_subscribe in verified_users.items():
            if not is_subscribe:
                notices.append(MNotice(user_id=user_id, text=UNSUBSCRIBE))
        await save_notices(notices)

    @classmethod
    async def update_positions(cls, track_id: int) -> tuple[str, int, Positions]:
        async with session_factory() as session:
            track = await TrackDao(session).find_one(id=track_id)
            query: MQuery = await track.awaitable_attrs.query
            parser = Parser(track.articule, query.query)
            position = await parser.get_positions()
            return query.query, track.articule, position[track.articule]

    @classmethod
    async def create_track(cls, query_text: str, articule: int, user_id: int) -> MTrack:
        async with session_factory() as session:
            query_dao = QueryDao(session)
            query = await query_dao.find_one_or_none(query=query_text)
            if not query:
                query = await query_dao.add(MQuery(query=query_text))
            track = await TrackDao(session).add(
                MTrack(articule=articule, user_id=user_id, query_id=query.id)
            )
        return track

    @classmethod
    async def update_track(cls, track_id: int, is_enable: bool) -> None:
        async with session_factory() as session:
            await TrackDao(session).update({"notice_enabled": is_enable}, id=track_id)

    @staticmethod
    async def get_all_tracks(**filter_by) -> Sequence[MQuery]:
        async with session_factory() as session:
            return await QueryDao(session).find_all_with_filter_by_track(**filter_by)

    @staticmethod
    async def _clear_notices() -> None:
        async with session_factory() as session:
            await NoticeDao(session).delete()

    @staticmethod
    async def _exclude_unsubscribed_users(
        verified_users: dict[int, bool],
        channel_id: str,
        tracks: dict[int, MTrack],
        bot: Bot,
    ) -> dict[int, MTrack]:
        valid_tracks = dict()
        for articule, track in tracks.items():
            if track.user_id not in verified_users:
                is_subscribe = await check_subscribe_on_channel(
                    channel_id, track.user_id, bot
                )
                verified_users[track.user_id] = is_subscribe
            if verified_users[track.user_id]:
                valid_tracks[articule] = track
        return valid_tracks


async def update_tracks(bot: Bot):
    channel_id = await get_channel_id()
    await Tracking.update_tracks_position(channel_id, bot)
