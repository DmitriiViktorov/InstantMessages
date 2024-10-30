from sqlalchemy import select

from database import SessionLocal
from auth.models import User


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_telegram_id_to_user(telegram_account: str, telegram_user_id: str):
    async with SessionLocal() as db:
        user_query = select(User).where(User.telegram_account == telegram_account)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()

        if user and user.telegram_id:
            return False, user

        user.telegram_id = telegram_user_id
        try:
            await db.commit()
            logger.info(f"Telegram ID {user.telegram_id} added for user {user.telegram_account}.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error when adding Telegram ID for user {user.telegram_account}: {e}")
        logger.info(f"User id {user.id}, user telegram id {user.telegram_id}")

        return True, user



async def remove_telegram_id_from_user(telegram_account: str):
    async with SessionLocal() as db:
        user_query = select(User).where(User.telegram_account == telegram_account)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()

        if user and not user.telegram_id:
            return False, user

        user.telegram_id = None
        try:
            await db.commit()
            logger.info(f"Telegram ID deleted to user {user.telegram_account}.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error when deleting Telegram ID для пользователя {user.telegram_account}: {e}")
        logger.info(f"User id {user.id}, user telegram id {user.telegram_id}")

        return True, user

