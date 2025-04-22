import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from redis.asyncio import Redis

from config_data import Config

from tg_bot.services.database import db_create_pool, db_create_need_tables, DB

# Импортируем роутеры
from tg_bot.handlers import commands, other_messages, auth, main_menu
# Импортируем миддлвари
from tg_bot.middlewares.commands_middleware import CommandsMiddleware
# Импортируем вспомогательные функции для создания нужных объектов
# ...
from tg_bot.keyboards import set_main_menu


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
    dp.workflow_data.update({'config': config, 'db': db})

    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # Регистриуем роутеры
    logger.info('Подключаем роутеры')
    dp.include_routers(commands.router, auth.router, main_menu.router, other_messages.router)

    # Регистрируем миддлвари
    logger.info('Подключаем миддлвари')
    commands.router.message.outer_middleware(CommandsMiddleware())

    # Пропускаем накопившиеся апдейты и запускаем polling
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
