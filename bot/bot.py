from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from config import BOT_TOKEN, REDIS_URL


from database.db import DataBaseSession
from database.engine import create_db, session_maker, drop_db

from handlers import setup_routers
from logging_config import setup_logging

from logging_middleware import LoggingMiddleware
from users_middleware import UsersMiddleware
import logging
import asyncio


async def main():
    bot = Bot(BOT_TOKEN)
    storage = RedisStorage.from_url(REDIS_URL, key_builder=DefaultKeyBuilder(with_destiny=True, with_bot_id=True))
    setup_logging()
    dp = Dispatcher(storage = storage)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    # await drop_db()
    await create_db()
    router = setup_routers()
    dp.include_router(router)
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(UsersMiddleware())
    print('Бот запущен и готов к приему сообщений')
    logging.info('--------------------Бот запущен и готов к приему сообщений------------------------------')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True)
    
    
if __name__ == "__main__":
    asyncio.run(main())
    