import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config_data import Config
from tg_bot.bot import TelegramBot
# Импортируем роутеры
from tg_bot.handlers import commands, other_messages, auth, main_menu, settings_menu, firstly, admin
from tg_bot.keyboards import set_main_menu
from async_logging import listener  # импортируем асинхронное логгирование
from tg_bot.middlewares.ban_check_middleware import BanCheckMiddleware
# Импортируем миддлвари
from tg_bot.middlewares.load_user_db_middleware import LoadUserDbMiddleware

from redis_service import redis_client_storage, redis

logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def start_tg_bot(config: Config):
    logger.info('Запускаем бота')


    storage = RedisStorage(redis=redis)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)


    telegram_bot = TelegramBot(config=config, redis=redis)

    dp.workflow_data.update(
        {'config': config, 'redis_client_storage': redis_client_storage, 'telegram_bot': telegram_bot})

    logger.info("Настраиваем меню у бота")
    await set_main_menu(bot)

    logger.info('Подключаем роутеры')
    dp.include_routers(firstly.router, commands.router, main_menu.router, auth.router,
                       settings_menu.router, admin.router, other_messages.router)

    logger.info('Подключаем миддлвари')
    dp.message.outer_middleware(BanCheckMiddleware())
    commands.router.message.outer_middleware(LoadUserDbMiddleware())

    logger.info("Запускаем поллинг")
    try:
        await dp.start_polling(bot)
    finally:
        # Корректно останавливаем listener при завершении
        listener.stop()
