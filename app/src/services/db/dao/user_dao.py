from sqlalchemy.dialects.postgresql import insert
from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.models import MUser


class UserDao(BaseDao[MUser]):
    model = MUser

    async def insert_or_nothing(
        self, user_id: int, fullname: str, username: str | None, source: str | None
    ):
        query = (
            insert(MUser)
            .values(id=user_id, fullname=fullname, username=username, source=source)
            .on_conflict_do_nothing(index_elements=["id"])
        )
        await self._session.execute(query)
        await self._session.commit()
