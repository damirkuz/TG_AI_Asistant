from database import DB, BotUserDB


async def get_user_db(db: DB, user_id: int, username: str = None) -> BotUserDB:
    user_record = await db.fetch_one("SELECT * FROM bot_users WHERE telegram_id = $1 OR username = $2", user_id, username)
    user_db = BotUserDB(**dict(user_record)) if user_record else None
    return user_db