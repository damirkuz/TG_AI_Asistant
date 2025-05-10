from dataclasses import dataclass

from redis import Redis

from config_data import Config
from database import DB


@dataclass
class TelegramBot:
    config: Config
    db: DB
    redis: Redis
