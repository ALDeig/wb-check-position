from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from app.src.services.user import get_my_tracks, user_start_process

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
        parse_mode=ParseMode.MARKDOWN_V2
    )


@router.callback_query(F.data == "articules", F.message.as_("message"))
async def btn_my_articules(call: CallbackQuery, message: Message):
    messages = await get_my_tracks(call.from_user.id)
    for text, kb in messages:
        await message.answer(text, reply_markup=kb)
