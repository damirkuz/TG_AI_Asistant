import logging

from database import DB, BotUserDB

logger = logging.getLogger(__name__)


async def get_user_db(db: DB, user_id: int, username: str = None) -> BotUserDB:
    logger.debug("Запрос пользователя из БД: user_id=%s, username=%s", user_id, username)
    user_record = await db.fetch_one("SELECT * FROM bot_users WHERE telegram_id = $1 OR username = $2", user_id,
                                     username)
    user_db = BotUserDB(**dict(user_record)) if user_record else None
    if user_db:
        logger.info("Пользователь найден в БД: user_id=%s, username=%s", user_id, username)
    else:
        logger.warning("Пользователь не найден в БД: user_id=%s, username=%s", user_id, username)
    return user_db
