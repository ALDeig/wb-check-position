

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.src.services.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    fullname: Mapped[str] = mapped_column(Text)
    username: Mapped[str | None] = mapped_column(Text, nullable=True)
