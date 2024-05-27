import logging
from collections import defaultdict
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
            tracks = cls._group_by_articles(query.tracks)
            if channel_id:
                tracks = await cls._exclude_unsubscribed_users(
                    verified_users, channel_id, tracks, bot
                )
                if not tracks:
                    continue
            parser = Parser(articules=list(tracks.keys()), query=query.query)
            positions = await parser.get_positions()
            for articule, group in tracks.items():
                for track in group:
                    notice = cls._prepare_notices(
                        track, articule, positions[articule], query.query
                    )
                    notices.append(notice)
            await save_notices(notices)
        notices = []
        for user_id, is_subscribe in verified_users.items():
            if not is_subscribe:
                notices.append(
                    MNotice(user_id=user_id, track_id=None, text=UNSUBSCRIBE)
                )
        await save_notices(notices)

    @classmethod
    async def update_positions(
        cls, track_id: int
    ) -> tuple[str, int, Positions, Positions | None]:
        async with session_factory() as session:
            track_dao = TrackDao(session)
            track = await track_dao.find_one(id=track_id)
            old_positions = (
                Positions.model_validate(track.positions) if track.positions else None
            )
            query: MQuery = await track.awaitable_attrs.query
            parser = Parser(track.articule, query.query)
            position = await parser.get_positions()
            await track_dao.update(
                {"positions": position[track.articule].model_dump()}, id=track_id
            )
            return query.query, track.articule, position[track.articule], old_positions

    @classmethod
    async def create_track(
        cls, query_text: str, articule: int, user_id: int, positions: dict
    ) -> MTrack:
        async with session_factory() as session:
            query_dao = QueryDao(session)
            query = await query_dao.find_one_or_none(query=query_text)
            if not query:
                query = await query_dao.add(MQuery(query=query_text))
            track = await TrackDao(session).add(
                MTrack(
                    articule=articule,
                    user_id=user_id,
                    query_id=query.id,
                    positions=positions,
                )
            )
        return track

    @classmethod
    async def update_status_tracking(cls, track_id: int, is_enable: bool) -> None:
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
    async def _prepare_notices(
        track: MTrack, articule: int, positions: Positions, query: str
    ) -> MNotice:
        old_positions = (
            Positions.model_validate(track.positions) if track.positions else None
        )
        text = get_tracking_text(query, articule, positions, old_positions)
        return MNotice(user_id=track.user_id, track_id=track.id, text=text)

    @staticmethod
    async def _exclude_unsubscribed_users(
        verified_users: dict[int, bool],
        channel_id: str,
        tracks: dict[int, list[MTrack]],
        bot: Bot,
    ) -> dict[int, list[MTrack]]:
        valid_tracks = dict()
        for articule, group in tracks.items():
            for track in group:
                if track.user_id not in verified_users:
                    is_subscribe = await check_subscribe_on_channel(
                        channel_id, track.user_id, bot
                    )
                    verified_users[track.user_id] = is_subscribe
                if not verified_users[track.user_id]:
                    group.remove(track)
            if group:
                valid_tracks[articule] = group
        return valid_tracks

    @staticmethod
    def _group_by_articles(tracks: list[MTrack]) -> dict[int, list[MTrack]]:
        group_tracks = defaultdict(list)
        for track in tracks:
            if track.notice_enabled:
                group_tracks[track.articule].append(track)
        return group_tracks


async def update_tracks(bot: Bot):
    channel_id = await get_channel_id()
    await Tracking.update_tracks_position(channel_id, bot)
