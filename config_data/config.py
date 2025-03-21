from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str
    db_host: str
    db_user: str
    db_password: str


@dataclass
class TgBot:
    token: str
    admin_ids: set[int]

@dataclass
class TGAppConfig:
    api_id: int
    api_hash: str


@dataclass
class Config:
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
            token=env("BOT_TOKEN"),
            admin_ids=set(map(int, env.list("ADMIN_IDS")))),
        db=DatabaseConfig(
            database=env("DATABASE"),
            db_host=("DB_HOST"),
            db_user=env("DB_USER"),
            db_password=env("DB_PASSWORD")))