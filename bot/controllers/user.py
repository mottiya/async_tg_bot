from typing import Optional
from loguru import logger

from aiogram.types import User as TgUser

from bot.models import User

async def get_user(from_user:TgUser, chat_id:int) -> User:
    user = await user_exists(from_user.id)
    if user is None:
        user = await User.create(
            user_id=from_user.id,
            chat_id=chat_id,
            username=from_user.username,
            full_name=from_user.full_name,
            admin_status=False)
        logger.info(f"New User: {user}")
    if user.chat_id is None:
        user.chat_id = chat_id
        await user.save(update_fields=['chat_id'])
    return user


async def user_exists(user_id: int) -> Optional[User]:
    user = await User.filter(user_id=user_id).first()
    if user:
        return user
    return None
