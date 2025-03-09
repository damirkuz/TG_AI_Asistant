from environs import Env
from dataclasses import dataclass

@dataclass
class TGConfig:
    api_id: int
    api_hash: str




def load_config() -> TGConfig:
    env = Env()
    env.read_env()
    return TGConfig(api_id=env.int("API_ID"), api_hash=env.str("API_HASH"))