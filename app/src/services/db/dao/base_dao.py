from typing import Generic, Sequence, TypeVar


import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.services.db.base import Base


TypeModel = TypeVar("TypeModel", bound=Base)


class BaseDao(Generic[TypeModel]):
    model: type[TypeModel]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_all(self, **filter_by) -> Sequence[TypeModel]:
        query = sa.select(self.model).filter_by(**filter_by)
        response = await self._session.scalars(query)
        return response.all()

    async def find_one_or_none(self, **filter_by) -> TypeModel | None:
        query = sa.select(self.model).filter_by(**filter_by)
        return await self._session.scalar(query)

    async def add(self, model_instanse: TypeModel) -> TypeModel:
        async with self._session.begin():
            self._session.add(model_instanse)
            return model_instanse

    async def delete(self, **filter_by) -> None:
        query = sa.delete(self.model).filter_by(**filter_by)
        await self._session.execute(query)
        await self._session.commit()
