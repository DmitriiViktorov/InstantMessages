import asyncpg
from aiogram import Bot, Dispatcher

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, BOT_TOKEN

tg_bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

async def get_db_pool():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )