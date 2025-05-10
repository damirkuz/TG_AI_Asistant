from datetime import datetime

from pydantic import BaseModel
from typing import Optional
__all__ = ["BotUserDB"]


class BotUserDB(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    full_name: Optional[str]
    is_admin: bool
    is_active: bool
    is_banned: bool
    created_at: Optional[datetime]
