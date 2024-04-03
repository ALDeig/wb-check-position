import asyncio
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
    set_start_message,
)

router = Router(name=__name__)


@router.message(Command("mailing"))
async def cmd_mailing(msg: Message, state: FSMContext):
    await msg.answer("Введите текст рассылки")
    await state.set_state("mailing")


@router.message(StateFilter("mailing"))
async def get_text_mailing(msg: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await mailing_to_users(cast(str, msg.text), bot)
    await msg.answer("Рассылка запущена")
    tasks = asyncio.all_tasks()
    for task in tasks:
        if task.get_name() == "mailing":
            await task
            await msg.answer("Рассылка завершена")


@router.message(Command("users"))
async def cmd_get_users(msg: Message):
    file = await get_file_with_users()
    await msg.answer_document(FSInputFile(file))


@router.message(Command("channel_check"))
async def cmd_change_channel_subscribe_check(msg: Message):
    kb = kb_change_state_check_subscribe()
    await msg.answer("Выберите состояние проверки подпски на канал", reply_markup=kb)


@router.callback_query(F.data.in_({"enable", "disable"}), F.data.as_("data"))
async def btn_change_check_subscribe(call: CallbackQuery, data: str):
    await call.answer()
    await change_state_check_subscribe(data)


@router.message(Command("set_start_text"))
async def cmd_set_start(msg: Message, state: FSMContext):
    await msg.answer("Введите сообщение")
    await state.set_state("get_msg_for_start")
    

@router.message(StateFilter("get_msg_for_start"))
async def get_start_text(msg: Message, state: FSMContext):
    await state.clear()
    await set_start_message(msg.md_text)


@router.message(Command("set_help_text"))
async def cmd_set_help_text(msg: Message, state: FSMContext):
    await msg.answer("Введите сообщение")
    await state.set_state("get_set_help_text")


@router.message(StateFilter("get_set_help_text"))
async def get_help_text(msg: Message, state: FSMContext):
    await state.clear()
    await set_start_message(msg.md_text)
