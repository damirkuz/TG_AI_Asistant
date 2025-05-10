from dataclasses import dataclass

from redis import Redis

from database import DB
from config_data import Config


@dataclass
class TelegramBot:
    config: Config
    db: DB
    redis: Redis
