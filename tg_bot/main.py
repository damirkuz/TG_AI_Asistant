import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config_data import Config
from database import db_create_pool, db_create_need_tables, DB
from tg_bot.bot import TelegramBot
# Импортируем роутеры
from tg_bot.handlers import commands, other_messages, auth, main_menu, settings_menu, firstly, admin
from tg_bot.keyboards import set_main_menu
from tg_bot.logging_settings.async_logging import setup_async_logging, listener  # импортируем асинхронное логгирование
from tg_bot.middlewares.ban_check_middleware import BanCheckMiddleware
# Импортируем миддлвари
from tg_bot.middlewares.load_user_db_middleware import LoadUserDbMiddleware
from tg_bot.services.redis_client_storage import RedisClientStorage

# Настраиваем асинхронное логгирование
setup_async_logging()

logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def start_tg_bot(config: Config):
    logger.info('Запускаем бота')

    logger.info('Подключаем redis')
    redis = Redis(host='localhost')
    redis_client_storage = RedisClientStorage(host='redis://localhost')

    storage = RedisStorage(redis=redis)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    logger.info('Настраиваем базу данных')
    pool = await db_create_pool(db_config=config.db)
    db = DB(pool=pool)
    await db_create_need_tables(db=db)

    telegram_bot = TelegramBot(config=config, db=db, redis=redis)

    dp.workflow_data.update(
        {'config': config, 'db': db, 'redis_client_storage': redis_client_storage, 'telegram_bot': telegram_bot})

    logger.info("Настраиваем меню у бота")
    await set_main_menu(bot)

    logger.info('Подключаем роутеры')
    dp.include_routers(firstly.router, commands.router, main_menu.router, admin.router, auth.router,
                       settings_menu.router, other_messages.router)

    logger.info('Подключаем миддлвари')
    dp.message.outer_middleware(BanCheckMiddleware())
    commands.router.message.outer_middleware(LoadUserDbMiddleware())

    logger.info("Запускаем поллинг")
    try:
        await dp.start_polling(bot)
    finally:
        # Корректно останавливаем listener при завершении
        listener.stop()
