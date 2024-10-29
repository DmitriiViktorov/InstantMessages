from database import SessionLocal
from auth.models import User
from sqlalchemy import select


async def get_user_id(telegram_account: str):
    query = select(User.first_name).where(User.telegram_account == telegram_account)
    async with SessionLocal() as db:
        result = await db.execute(query)
    user_first_name = result.scalar_one_or_none()

    return user_first_name
