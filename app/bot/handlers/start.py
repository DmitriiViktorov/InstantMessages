from aiogram import types, Router
from aiogram.filters.command import Command
from bot.create_bot import dp
from bot.utils.database_queries import get_user_id

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: types.Message):
    telegram_account = message.from_user.username

    user_first_name = await get_user_id(telegram_account=telegram_account)

    await message.answer(f"Hello {message.from_user.username}! Ваш chat_id: {message.chat.id}, ваше first_name: {user_first_name}")

