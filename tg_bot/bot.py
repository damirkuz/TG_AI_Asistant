from dataclasses import dataclass

from redis import Redis

from config_data import Config


@dataclass
class TelegramBot:
    config: Config
    redis: Redis
