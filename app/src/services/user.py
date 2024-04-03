from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

from app.src.dialog.keyboards.tracking import kb_after_query, remove_track
from app.src.dialog.keyboards.user import user_menu
from app.src.services.db.base import session_factory
from app.src.services.db.dao.settings_dao import SettingDao
from app.src.services.db.dao.user_dao import UserDao
from app.src.services.db.models import SettingKeys
from app.src.services.texts.tracking import get_text_track, get_tracking_text
from app.src.services.texts.user import ARTICULE_NOT_FOUND, HELP, START_TEXT
from app.src.services.tracking.tracking import Tracking
from app.src.services.wb.parser import Parser, get_article


async def user_start_process(
    user_id: int, fullname: str, username: str | None, source: str | None
) -> tuple[str, InlineKeyboardMarkup]:
    """На команду старт. Сохраняет пользователя в БД"""
    async with session_factory() as session:
        await UserDao(session).insert_or_nothing(
            user_id=user_id, fullname=fullname, username=username, source=source
        )
        text = await SettingDao(session).find_one_or_none(key=SettingKeys.START_MESSAGE)
        start_text = text.value if text and text.value else START_TEXT
    return start_text, user_menu()


async def new_query(user_id: int, raw_query: str) -> tuple[str, InlineKeyboardMarkup]:
    """На прислынный запрос. Запрашивает позиции и создает трек, без отслеживания"""
    articule, query = _get_articule_and_query(raw_query)
    parser = Parser(articule, query)
    if not await parser.is_exists():
        return ARTICULE_NOT_FOUND, user_menu()
    product = await parser.get_positions()
    track = await Tracking.create_track(query, articule, user_id)
    text = get_tracking_text(query, articule, product[articule])
    kb = kb_after_query(track.id)
    return text, kb


async def update_query_positions(track_id: int) -> tuple[str, InlineKeyboardMarkup]:
    """На кнопку обновить. Обновление позиций и присылает новые"""
    query, articule, positions = await Tracking.update_positions(track_id)
    text = get_tracking_text(query, articule, positions)
    kb = kb_after_query(track_id)
    return text, kb


async def check_subscribe_channel(user_id: int, bot: Bot) -> bool:
    """Проверяет подписку на калан"""
    async with session_factory() as session:
        settings_dao = SettingDao(session)
        is_enable = await settings_dao.find_one_or_none(key=SettingKeys.CHECK_IS_ENABLE)
        if is_enable is None or is_enable.value is None or is_enable.value == "disable":
            return True
        channel = await settings_dao.find_one_or_none(key=SettingKeys.CHANNEL)
        if channel is None or channel.value is None:
            return True
        chat_member = await bot.get_chat_member(channel.value, user_id)
        print(chat_member)
        return True


async def get_my_tracks(user_id: int) -> list[tuple[str, InlineKeyboardMarkup]]:
    """На кнопку мои отслеживания. Возвращает список кортежей,
    с текстом и клавиатурой"""
    messages = []
    queries = await Tracking.get_all_tracks(notice_enabled=True, user_id=user_id)
    for query in queries:
        for track in query.tracks:
            if track.notice_enabled:
                text = get_text_track(query.query, track.articule)
                kb = remove_track(track.id)
                messages.append((text, kb))
    return messages


async def get_help_message() -> tuple[str, InlineKeyboardMarkup]:
    async with session_factory() as session:
        text = await SettingDao(session).find_one_or_none(key=SettingKeys.HELP_MESSAGE)
        help_text = text.value if text and text.value else HELP
    return help_text, user_menu()


async def change_notify_state(track_id: int, state: bool):
    await Tracking.update_track(track_id, state)


def _get_articule_and_query(full_query: str) -> tuple[int, str]:
    articule_or_url, query = full_query.split(maxsplit=1)
    return get_article(articule_or_url), query.strip()
