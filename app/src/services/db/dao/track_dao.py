from typing import Sequence

import sqlalchemy as sa

from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.models import MNotice, MQuery, MTrack


class QueryDao(BaseDao[MQuery]):
    model = MQuery

    async def find_all_with_filter_by_track(self, **filter_by) -> Sequence[MQuery]:
        query = (
            sa.select(self.model)
            .join(MTrack, MTrack.query_id == MQuery.id)
            .filter_by(**filter_by)
        )
        response = await self._session.scalars(query)
        return response.unique().all()


class TrackDao(BaseDao[MTrack]):
    model = MTrack

    async def count(self, **filter_by) -> int:
        query = sa.select(sa.func.count(self.model.id)).filter_by(**filter_by)
        return (await self._session.execute(query)).scalar_one()


class NoticeDao(BaseDao[MNotice]):
    model = MNotice

    async def add_all(self, notices: list[MNotice]):
        self._session.add_all(notices)
        await self._session.commit()
