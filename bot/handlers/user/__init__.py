from aiogram import Dispatcher

from .handlers import router
from .config_search.handlers import cfsch_router

async def setup(dp: Dispatcher):
    # Commands
    dp.include_router(router)
    dp.include_router(cfsch_router)
