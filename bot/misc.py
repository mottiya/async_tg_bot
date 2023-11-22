import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config import TELEGRAM_BOT_TOKEN

ROOT_DIR: Path = Path(__file__).parent.parent
admin_ref = '@avtopad'
max_demo_notifi = 10

loop = asyncio.get_event_loop()
storage = MemoryStorage()

bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)

async def setup():
    user = await bot.me()
    logger.info(f"Bot: {user.full_name} [@{user.username}]")
    logger.debug(f'{ROOT_DIR=}')
