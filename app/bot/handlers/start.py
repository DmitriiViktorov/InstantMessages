from aiogram import types, Router
from aiogram.filters.command import Command
from bot.utils.database_queries import (
    add_telegram_id_to_user,
    remove_telegram_id_from_user
)

start_router = Router()


@start_router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"Hello {message.from_user.username}! I`m a InstantMessages bot.\n"
                         f"If you want to start subscription, run the /subscribe command.\n"
                         f"If you want to cancel your subscription, run the /unsubscribe command.")


@start_router.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    telegram_account, telegram_id = message.from_user.username, str(message.chat.id)
    subscription, user = await add_telegram_id_to_user(telegram_account, telegram_id)
    if subscription and user:
        await message.answer(f"Hello {user.full_name}!\n"
                             f"You have subscribed to receive notifications "
                             f"of new messages from InstantMessages.")

    elif (not subscription) and user:
        await message.answer(f"Hello {user.full_name}! "
                             f"You already have a subscription for notifications "
                             f"of new messages in Instant Messages.\n"
                             f"If you want to cancel your subscription, run the /unsubscribe command.")

    else:
        await message.answer(f"Hello {telegram_account}!\n"
                             f"Something went wrong when subscribing. \n"
                             f"We have not found your account. \n"
                             f"Make sure that your telegram account is listed in your profile.")


@start_router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: types.Message):
    telegram_account = message.from_user.username
    unsubscription, user = await remove_telegram_id_from_user(telegram_account)

    if unsubscription and user:
        await message.answer(f"Hello {user.full_name}! "
                             f"You have successfully unsubscribed from notifications "
                             f"of new messages in Instant Messages.\n"
                             f"If you want to restore your subscription, run the /subscribe command.")

    elif (not unsubscription) and user:
        await message.answer(f"Hello {user.full_name}! You do not have a subscription for notification "
                             f"of new messages in Instant Messages.\n"
                             f"If you want to start subscription, run the /subscribe command.")
    else:
        await message.answer(f"Hello {telegram_account}!\n"
                             f"Something went wrong when subscribing. \n"
                             f"We have not found your account. \n"
                             f"Make sure that your telegram account is listed in your profile.")