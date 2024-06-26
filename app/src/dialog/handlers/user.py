from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from app.src.services.texts.user import NOT_FOUND_ARTICULES
from app.src.services.user import get_help_message, get_my_tracks, user_start_process

router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(msg: Message, command: CommandObject):
    text, kb = await user_start_process(
        msg.chat.id, msg.chat.full_name, msg.chat.username, command.args
    )
    await msg.answer(
        text=text,
        reply_markup=kb,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@router.callback_query(F.data == "articules", F.message.as_("message"))
async def btn_my_articules(call: CallbackQuery, message: Message):
    await call.answer(cache_time=30)
    messages = await get_my_tracks(call.from_user.id)
    if not messages:
        await message.answer(NOT_FOUND_ARTICULES)
    for text, kb in messages:
        await message.answer(text, reply_markup=kb)


@router.message(Command("my_articles"))
async def cmd_my_articles(msg: Message) -> None:
    messages = await get_my_tracks(msg.chat.id)
    if not messages:
        await msg.answer(NOT_FOUND_ARTICULES)
    for text, kb in messages:
        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data == "help", F.message.as_("message"))
async def btn_help(call: CallbackQuery, message: Message):
    await call.answer()
    help_text, kb = await get_help_message()
    await message.answer(
        help_text,
        reply_markup=kb,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
