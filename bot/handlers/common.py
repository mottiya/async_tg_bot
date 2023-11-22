from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Dispatcher

import bot.text as text

router_common = Router()

async def setup(dp: Dispatcher):
    # Commands
    dp.include_router(router_common)

@router_common.message()
async def cap(msg: Message, state: FSMContext):
    await msg.answer(text.cap)