from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message

from app.src.services.texts.user import UNSUBSCRIBE
from app.src.services.user import (
    change_notify_state,
    check_subscribe_channel,
    new_query,
    update_query_positions,
)

router = Router()


@router.message(F.text.as_("text"))
async def get_query(msg: Message, bot: Bot, text: str) -> None:
    """Хендлер получает запрос на показ позици."""
    if not await check_subscribe_channel(msg.chat.id, bot):
        await msg.answer(UNSUBSCRIBE)
        return
    responses = await new_query(msg.chat.id, text)
    for response_text, kb in responses:
        await msg.answer(response_text, reply_markup=kb)


@router.callback_query(
    F.data.startswith("update"), F.data.as_("data"), F.message.as_("message")
)
async def btn_update(
    call: CallbackQuery, bot: Bot, data: str, message: Message
) -> None:
    await call.answer(cache_time=30)
    if not await check_subscribe_channel(message.chat.id, bot):
        await message.answer(UNSUBSCRIBE)
        return
    _, track_id = data.split(":")
    text, kb = await update_query_positions(int(track_id))
    await message.answer(text, reply_markup=kb)


@router.callback_query(
    F.data.startswith("add") | F.data.startswith("remove"),
    F.data.as_("data"),
    F.message.as_("msg"),
)
async def btn_change_notify_state(
    call: CallbackQuery, bot: Bot, data: str, msg: Message
) -> None:
    if not await check_subscribe_channel(msg.chat.id, bot):
        await msg.answer(UNSUBSCRIBE)
        return
    action, track_id = data.split(":")
    await change_notify_state(int(track_id), notify_state=(action == "add"))
    # await change_notify_state(int(track_id), )
    if isinstance(call.message, Message):
        await call.message.answer("Готово")
