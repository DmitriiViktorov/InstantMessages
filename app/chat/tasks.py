import os
import asyncio
from celery import Celery
from bot.create_bot import tg_bot
import logging


logging.basicConfig(level=logging.INFO)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://cache:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://cache:6379")

async def send_notification(current_user_full_name, other_user_telegram_id):
    logging.info(f"Sending message to {other_user_telegram_id}: User {current_user_full_name} sent you a message.")
    try:
        await tg_bot.send_message(
            chat_id=other_user_telegram_id,
            text=f"User {current_user_full_name} send you a message. Check your InstantMessages chats."
        )
    except Exception as e:
        logging.error(f"Failed to send message: {e}")


@celery.task(name="notification")
def notification(current_user_full_name: str, other_user_telegram_id: str):
    loop = asyncio.get_event_loop()
    task = loop.create_task(send_notification(current_user_full_name, other_user_telegram_id))
    loop.run_until_complete(task)
