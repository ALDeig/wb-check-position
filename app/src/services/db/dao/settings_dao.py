from sqlalchemy.dialects.postgresql import insert
from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.models import MSettings


class SettingDao(BaseDao[MSettings]):
    model = MSettings

    async def insert_or_update(self, values: dict[str, str]):
        query = (
            insert(self.model)
            .values(values)
            .on_conflict_do_update(
                index_elements=["key"], set_={"value": values["value"]}
            )
        )
        await self._session.execute(query)
        await self._session.commit()
