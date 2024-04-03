from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from app.src.services.user import change_notify_state, new_query, update_query_positions


router = Router()


@router.message(F.text.as_("text"))
async def get_query(msg: Message, text: str):
    """Хендлер получает запрос на показ позици"""
    text, kb = await new_query(msg.chat.id, text)
    await msg.answer(text, reply_markup=kb)


@router.callback_query(
    F.data.startswith("update"), F.data.as_("data"), F.message.as_("message")
)
async def btn_update(call: CallbackQuery, data: str, message: Message):
    await call.answer(cache_time=30)
    _, track_id = data.split(":")
    text, kb = await update_query_positions(int(track_id))
    await message.answer(text, reply_markup=kb)


@router.callback_query(
    F.data.startswith("add") | F.data.startswith("remove"), F.data.as_("data")
)
async def btn_change_notify_state(call: CallbackQuery, data: str):
    action, track_id = data.split(":")
    await change_notify_state(int(track_id), action == "add")
    if isinstance(call.message, Message):
        await call.message.answer("Готово")
