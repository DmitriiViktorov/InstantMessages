from datetime import datetime, timezone
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from sqlalchemy.orm import joinedload

from .models import Message


def cache_ignore_db(expire: int):
    def wrapper(func):
        async def wrapped(*args, **kwargs):
            cache_kwargs = {k: v for k, v in kwargs.items() if k != 'db'}
            cache_key = f"chat_cache:{kwargs['current_user_id']}"

            @cache(expire=expire, key_builder=lambda *a, **k: cache_key)
            async def cached_func(*args, **kwargs):
                return await func(*args, **kwargs)

            return await cached_func(*args, **kwargs)
        return wrapped
    return wrapper


@cache_ignore_db(expire=60)
async def get_all_chats(
        current_user_id: int,
        db: AsyncSession,
):
    chats = []
    all_users_query = select(User.id, User.telegram_account).where(User.id != current_user_id)
    all_users_result = await db.execute(all_users_query)
    all_users = all_users_result.fetchall()

    for other_user in all_users:
        last_message_query = select(Message).where(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == other_user.id)) |
            ((Message.sender_id == other_user.id) & (Message.receiver_id == current_user_id))
        ).order_by(Message.created_at.desc()).limit(1)

        last_message_result = await db.execute(last_message_query)
        last_message = last_message_result.scalar_one_or_none()

        chats.append({
            "chat_id": other_user.id,
            "telegram_account": other_user.telegram_account,
            "last_message": last_message
        })

    min_datetime = datetime.min.replace(tzinfo=timezone.utc)

    chats.sort(key=lambda x: x["last_message"].created_at if x["last_message"] else min_datetime, reverse=True)

    return chats


async def get_chat_messages(
        current_user_id: int,
        other_user_id: int,
        db: AsyncSession,
):
    messages_query = select(Message).filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user_id))
    ).order_by(Message.created_at).options(joinedload(Message.sender),joinedload(Message.receiver))
    result = await db.execute(messages_query)

    return result.scalars().all()


async def get_user_by_id(user_id: int, db: AsyncSession):
    other_user_query = select(User).where(User.id == user_id)
    other_user_result = await db.execute(other_user_query)
    return other_user_result.scalar_one_or_none()