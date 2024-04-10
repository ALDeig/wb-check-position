import datetime
from enum import Enum

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.src.services.db.base import Base


class SettingKeys(str, Enum):
    START_MESSAGE = "start_message"
    CHECK_IS_ENABLE = "check_is_enable"
    CHANNEL = "channel"
    HELP_MESSAGE = "help_message"


def get_utc_time() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class MUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    fullname: Mapped[str] = mapped_column(Text)
    username: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)


class MQuery(Base):
    __tablename__ = "queries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(Text, index=True)

    tracks: Mapped[list["MTrack"]] = relationship(
        lazy="selectin", back_populates="query"
    )


class MTrack(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    articule: Mapped[int] = mapped_column(BigInteger)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    query_id: Mapped[int] = mapped_column(ForeignKey("queries.id", ondelete="CASCADE"))
    notice_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_time
    )

    query: Mapped["MQuery"] = relationship(back_populates="tracks")


class MNotice(Base):
    __tablename__ = "notices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text)
    track_id: Mapped[int] = mapped_column(
        ForeignKey("tracks.id", ondelete="CASCADE"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))


class MSettings(Base):
    __tablename__ = "settings"

    key: Mapped[SettingKeys] = mapped_column(Text, primary_key=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
