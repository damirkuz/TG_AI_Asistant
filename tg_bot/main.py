import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from redis.asyncio import Redis

from config_data import Config
from tg_bot.middlewares.ban_check_middleware import BanCheckMiddleware

from tg_bot.services.database import db_create_pool, db_create_need_tables, DB

# Импортируем роутеры
from tg_bot.handlers import commands, other_messages, auth, main_menu, settings_menu, firstly, admin
# Импортируем миддлвари
from tg_bot.middlewares.load_user_db_middleware import LoadUserDbMiddleware
# Импортируем вспомогательные функции для создания нужных объектов
# ...
from tg_bot.keyboards import set_main_menu
from tg_bot.services.redis_client_storage import RedisClientStorage

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def start_tg_bot(config: Config):
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Инициализируем Redis
    redis = Redis(host='localhost')
    redis_client_storage = RedisClientStorage(host='redis://localhost')

    # Инициализируем объект хранилища
    storage = RedisStorage(redis=redis)

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    # Инициализируем другие объекты (пул соединений с БД, кеш и т.п.)
    pool = await db_create_pool(db_config=config.db)
    db = DB(pool=pool)
    await db_create_need_tables(db=db)

    # Помещаем нужные объекты в workflow_data диспетчера
    dp.workflow_data.update({'config': config, 'db': db, 'redis_client_storage': redis_client_storage})

    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # Регистриуем роутеры
    logger.info('Подключаем роутеры')
    dp.include_routers(firstly.router, commands.router, main_menu.router, admin.router, auth.router, settings_menu.router, other_messages.router)

    # Регистрируем миддлвари
    logger.info('Подключаем миддлвари')

    dp.message.outer_middleware(BanCheckMiddleware())
    commands.router.message.outer_middleware(LoadUserDbMiddleware())

    # Пропускаем накопившиеся апдейты и запускаем polling
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
