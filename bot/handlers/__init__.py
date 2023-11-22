from aiogram import Dispatcher

# from . import errors
from . import admin
from . import user
from . import common


async def setup(dp: Dispatcher):
    # await errors.setup(dp)
    await user.setup(dp)
    await admin.setup(dp)
    await common.setup(dp)
