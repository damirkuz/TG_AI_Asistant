from environs import Env
from pydantic import BaseModel

__all__ = ["DatabaseConfig", "Config", "load_config", "TGAppConfig", "get_database_url", "get_sync_database_url"]


class DatabaseConfig(BaseModel):
    database: str
    db_host: str
    db_user: str
    db_password: str


class TgBot(BaseModel):
    token: str


class TGAppConfig(BaseModel):
    api_id: int
    api_hash: str


class Config(BaseModel):
    tg_app: TGAppConfig
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_app=TGAppConfig(
            api_id=int(env("TG_APP_API_ID")),
            api_hash=env("TG_APP_API_HASH"),
        ),
        tg_bot=TgBot(
            token=env("BOT_TOKEN")),
        db=DatabaseConfig(
            database=env("DATABASE"),
            db_host=env("DB_HOST"),
            db_user=env("DB_USER"),
            db_password=env("DB_PASSWORD")))


def get_database_url() -> str:
    config = load_config()
    url = "postgresql+asyncpg://{user}:{password}@{host}:5432/{db_name}".format(
        user=config.db.db_user,
        password=config.db.db_password,
        host=config.db.db_host,
        db_name=config.db.database)
    return url


def get_sync_database_url() -> str:
    config = load_config()
    url = "postgresql://{user}:{password}@{host}:5432/{db_name}".format(
        user=config.db.db_user,
        password=config.db.db_password,
        host=config.db.db_host,
        db_name=config.db.database)
    return url
