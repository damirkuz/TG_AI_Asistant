import logging
from typing import List

from sqlalchemy import select, update, func, or_, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from telethon import TelegramClient

from database import BotUserDB
from database.db_core import async_session_maker  # Фабрика сессий
from database.models import BotUser, TGAccount, AccountSession, Statistic
import database.models
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)


async def save_auth(
        client: TelegramClient,
        bot_user_id: int,
        password: str = None
) -> None:
    """
    Сохраняет или обновляет данные аутентификации телеграм-аккаунта в базе данных и Redis.
    """

    # Заносим в базу данных
    try:
        about_me = await client.get_me()
        tg_user_id = int(about_me.id)
        full_name = ' '.join(
            filter(
                None, [
                    about_me.first_name, about_me.last_name])).strip()
        phone_number = about_me.phone
        if phone_number:
            phone_number = ''.join(filter(str.isdigit, phone_number)) or None

        async with async_session_maker() as session:
            # TGAccount upsert
            stmt = insert(TGAccount).values(
                tg_user_id=tg_user_id,
                full_name=full_name,
                phone_number=phone_number
            ).on_conflict_do_update(
                index_elements=[TGAccount.tg_user_id],
                set_={
                    "full_name": full_name,
                    "phone_number": phone_number
                }
            ).returning(TGAccount.id)
            result = await session.execute(stmt)
            tg_account_id = result.scalar_one()


            # AccountSession upsert
            stmt2 = insert(AccountSession).values(
                bot_user_id=bot_user_id,
                tg_account_id=tg_account_id,
                session_data=StringSession.save(client.session),
                password=password).on_conflict_do_update(
                index_elements=[
                    AccountSession.bot_user_id,
                    AccountSession.tg_account_id],
                set_={
                    "session_data": StringSession.save(client.session),
                    "password": password})
            await session.execute(stmt2)
            await session.commit()
            logger.info(
                "Данные аутентификации сохранены для bot_user_id=%s, tg_account_id=%s",
                bot_user_id,
                tg_account_id)

    except SQLAlchemyError as e:
        logger.error(
            "Ошибка базы данных при сохранении аутентификации: %s",
            str(e))
        raise ValueError(f"Ошибка базы данных: {str(e)}") from e
    except Exception as e:
        logger.error("Ошибка сохранения данных аутентификации: %s", str(e))
        raise ValueError(f"Ошибка сохранения данных: {str(e)}") from e

    # Заносим в Redis
    from redis_service import redis_client_storage
    await redis_client_storage.save_session(user_id=bot_user_id, client=client)


async def save_bot_user(
        telegram_id: int,
        full_name: str,
        username: str | None = None,
        is_admin: bool = False,
        is_active: bool = True,
        is_banned: bool = False,
) -> int:
    """
    Сохраняет или обновляет пользователя бота в таблице bot_users.
    """
    try:
        async with async_session_maker() as session:
            stmt = insert(BotUser).values(
                telegram_id=telegram_id,
                full_name=full_name.strip(),
                username=username,
                is_admin=is_admin,
                is_active=is_active,
                is_banned=is_banned
            ).on_conflict_do_update(
                index_elements=[BotUser.telegram_id],
                set_={
                    "full_name": full_name.strip(),
                    "username": username,
                    "is_active": is_active,
                    "is_banned": is_banned
                }
            ).returning(BotUser.id)
            result = await session.execute(stmt)
            user_id = result.scalar_one()
            await session.commit()
            logger.info(
                "Пользователь telegram_id=%s успешно сохранён/обновлён",
                telegram_id)
            return user_id

    except SQLAlchemyError as e:
        logger.error(
            "Ошибка базы данных при сохранении пользователя: %s",
            str(e))
        raise ValueError(f"Ошибка базы данных: {str(e)}") from e
    except Exception as e:
        logger.error(
            "Неожиданная ошибка при сохранении пользователя: %s",
            str(e))
        raise ValueError(f"Неожиданная ошибка: {str(e)}") from e


async def get_bot_statistics() -> dict:
    """
    Получает статистику о пользователях бота
    """

    interval_str = '1 day'
    async with async_session_maker() as session:
        registered_users = await session.scalar(select(func.count()).select_from(BotUser))
        connected_accounts = await session.scalar(select(func.count()).select_from(TGAccount))
        total_activity = await session.scalar(select(func.count()).select_from(Statistic))
        daily_activity = await session.scalar(
            select(func.count()).select_from(Statistic).where(
                Statistic.created_at >= func.now() - text(f"interval '{interval_str}'")
            )
        )

        return {
            "registered_users": registered_users,
            "connected_accounts": connected_accounts,
            "total_activity": total_activity,
            "daily_activity": daily_activity
        }


# async def get_user_tg_id_in_db(user_message: Message) -> BotUserDB | None:
#     """
#     Проверяет есть ли пользователь в базе данных (bot_users), возвращает его BotUserDB
#     """
#     telegram_id = None
#     username = None
#     if user_message.contact:
#         telegram_id = user_message.contact.id
#     elif user_message.text.isdigit():
#         telegram_id = int(user_message.text)
#     elif user_message.text.startswith('@'):
#         username = user_message.text.lstrip('@')
#
#     async with async_session_maker() as session:
#         if telegram_id:
#             stmt = select(BotUser).where(BotUser.telegram_id == telegram_id)
#         elif username:
#             stmt = select(BotUser).where(BotUser.username == username)
#         else:
#             return None
#         result = await session.execute(stmt)
#         bot_user = result.scalar_one_or_none()
#         if bot_user:
#             logger.info(
#                 "Пользователь найден в базе: telegram_id=%s, username=%s",
#                 telegram_id,
#                 username)
#         else:
#             logger.warning(
#                 "Пользователь не найден в базе: telegram_id=%s, username=%s",
#                 telegram_id,
#                 username)
#         return BotUserDB.model_validate(bot_user) if bot_user else None


async def get_user_detailed(telegram_id: int) -> dict | None:
    """
    Возвращает подробную информацию о пользователе из базы
    """
    async with async_session_maker() as session:
        result1 = await session.execute(select(BotUser).where(BotUser.telegram_id == telegram_id))
        bot_user = result1.scalar_one_or_none()
        if not bot_user:
            return None
        result2 = await session.execute(select(TGAccount).where(TGAccount.tg_user_id == bot_user.telegram_id))
        tg_account = result2.scalar_one_or_none()
        merged = {
            "bot_user": {
                "id": bot_user.id,
                "telegram_id": bot_user.telegram_id,
                "username": bot_user.username,
                "full_name": bot_user.full_name,
                "is_admin": bot_user.is_admin,
                "is_active": bot_user.is_active,
                "is_banned": bot_user.is_banned,
                "created_at": bot_user.created_at,
            },
            "tg_account": {
                "id": tg_account.id,
                "tg_user_id": tg_account.tg_user_id,
                "full_name": tg_account.full_name,
                "phone_number": tg_account.phone_number,
                "created_at": tg_account.created_at,
            } if tg_account else None
        }
        logger.info(
            "Подробная информация о пользователе telegram_id=%s получена",
            telegram_id)
        return merged


async def ban_bot_user(telegram_id: int, ban: bool = True) -> None:
    async with async_session_maker() as session:
        stmt = update(BotUser).where(
            BotUser.telegram_id == telegram_id).values(
            is_banned=ban)
        await session.execute(stmt)
        await session.commit()
        from tg_bot.middlewares.ban_check_middleware import BanCheckMiddleware
        BanCheckMiddleware.clear_user_cache(telegram_id)
        logger.info(
            "Изменение статуса бана для пользователя telegram_id=%s -> %s",
            telegram_id,
            ban)


async def make_admin_bot_user(
        telegram_id: int,
        make_admin: bool = True) -> None:
    async with async_session_maker() as session:
        stmt = update(BotUser).where(
            BotUser.telegram_id == telegram_id).values(
            is_admin=make_admin)
        await session.execute(stmt)
        await session.commit()
        logger.info(
            "Изменение статуса администратора для пользователя telegram_id=%s -> %s",
            telegram_id,
            make_admin)


async def delete_user_in_db(telegram_id: int) -> None:
    async with async_session_maker() as session:
        stmt = select(BotUser).where(BotUser.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()
            logger.info(
                "Удаление пользователя из базы telegram_id=%s",
                telegram_id)


async def get_user_db(
        user_id: int = None,
        username: str = None) -> BotUserDB | None:
    logger.debug(
        "Запрос пользователя из БД: user_id=%s, username=%s",
        user_id,
        username)
    async with async_session_maker() as session:
        # Формируем условия динамически
        conditions = []
        if user_id is not None:
            conditions.append(BotUser.telegram_id == user_id)
        if username is not None:
            conditions.append(BotUser.username == username)

        if not conditions:
            logger.warning("Не передан ни user_id, ни username")
            return None

        stmt = select(BotUser).where(
            or_(*conditions)) if len(conditions) > 1 else select(BotUser).where(*conditions)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            logger.info(
                "Пользователь найден в БД: user_id=%s, username=%s",
                user_id,
                username)
        else:
            logger.warning(
                "Пользователь не найден в БД: user_id=%s, username=%s",
                user_id,
                username)
        return BotUserDB.model_validate(user, from_attributes=True) if user else None


async def add_users_chats(bot_user_id: int, chats: List[dict]) -> None:
    for chat in chats:
        chat['user_id'] = bot_user_id
        chat['last_updated'] = func.now()

    async with async_session_maker() as session:
        stmt = insert(database.models.Chat).values(chats)

        # Указываем действие при конфликте по chat_id
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['chat_id'],  # Уникальный индекс/первичный ключ
            set_={
                'title': stmt.excluded.title,
                'type': stmt.excluded.type,
                'last_updated': func.now()
            })

        await session.execute(upsert_stmt)
        await session.commit()


async def check_have_connected_account(bot_user_id: int) -> bool:
    async with async_session_maker() as session:
        stmt = select(AccountSession).where(AccountSession.bot_user_id == bot_user_id)
        result = (await session.execute(stmt)).scalar_one_or_none()
        if result:
            return True

