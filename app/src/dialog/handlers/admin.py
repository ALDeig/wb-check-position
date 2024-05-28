from typing import cast

from aiogram import Bot, F, Router
from aiogram.filters.command import Command
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.src.dialog.keyboards.admin import kb_change_state_check_subscribe
from app.src.services.admin import (
    change_state_check_subscribe,
    get_file_with_users,
    mailing_to_users,
    set_channel_for_check_subscribe,
    set_help_message,
    set_start_message,
)
from app.src.services.texts.admin import (
    CMD_CHECK_SUBSCRIBE,
    CMD_HELP_TEXT,
    CMD_MAILING,
    CMD_START_TEXT,
    END_MAILING,
    GET_ID_CHANNEL,
    READY,
    START_MAILING,
)

router = Router(name=__name__)


@router.message(Command("mailing"))
async def cmd_mailing(msg: Message, state: FSMContext):
    await msg.answer(CMD_MAILING)
    await state.set_state("mailing")


@router.message(StateFilter("mailing"))
async def get_text_mailing(msg: Message, bot: Bot, state: FSMContext):
    await state.clear()
    task = await mailing_to_users(cast(str, msg.text), bot)
    await msg.answer(START_MAILING)
    await task
    await msg.answer(END_MAILING)


@router.message(Command("users"))
async def cmd_get_users(msg: Message):
    file = await get_file_with_users()
    await msg.answer_document(FSInputFile(file))


@router.message(Command("channel_check"))
async def cmd_change_channel_subscribe_check(msg: Message):
    kb = kb_change_state_check_subscribe()
    await msg.answer(CMD_CHECK_SUBSCRIBE, reply_markup=kb)


@router.callback_query(
    F.data.in_({"enable", "disable"}), F.data.as_("data"), F.message.as_("message")
)
async def btn_change_check_subscribe(call: CallbackQuery, data: str, message: Message):
    await call.answer()
    text = await change_state_check_subscribe(data)
    await message.edit_text(text)


@router.message(Command("set_channel"))
async def cmd_set_channel_for_check_subscribe(msg: Message, state: FSMContext):
    await msg.answer(GET_ID_CHANNEL)
    await state.set_state("get_channel_id")


@router.message(StateFilter("get_channel_id"), F.text.as_("text"))
async def get_channel_id(msg: Message, state: FSMContext, text: str):
    await state.clear()
    await set_channel_for_check_subscribe(text)
    await msg.answer(READY)


@router.message(Command("set_start_text"))
async def cmd_set_start(msg: Message, state: FSMContext):
    await msg.answer(CMD_START_TEXT)
    await state.set_state("get_msg_for_start")


@router.message(StateFilter("get_msg_for_start"))
async def get_start_text(msg: Message, state: FSMContext):
    await state.clear()
    await set_start_message(msg.md_text)
    await msg.answer(READY)


@router.message(Command("set_help_text"))
async def cmd_set_help_text(msg: Message, state: FSMContext):
    await msg.answer(CMD_HELP_TEXT)
    await state.set_state("get_set_help_text")


@router.message(StateFilter("get_set_help_text"))
async def get_help_text(msg: Message, state: FSMContext):
    await state.clear()
    await set_help_message(msg.md_text)
    await msg.answer(READY)
