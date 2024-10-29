import asyncio

from create_bot import get_db_pool, dp, tg_bot
from bot.handlers.start import start_router


async def main():
    db_pool = await get_db_pool()
    dp.database = db_pool
    dp.include_routers(
        start_router
    )
    try:
        await dp.start_polling(tg_bot, close_bot_session=False)

    finally:
        await db_pool.close()



if __name__ == "__main__":
    asyncio.run(main())
