from aiogram import Dispatcher

from .handlers import router_admin

async def setup(dp: Dispatcher):
    # Commands
    dp.include_router(router_admin)