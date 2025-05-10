from dataclasses import dataclass
from pydantic import BaseModel
from environs import Env

__all__ = ["DatabaseConfig", "Config", "load_config", "TGAppConfig"]



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
