from pydantic import BaseModel
from typing import Optional
__all__ = ["UserDB"]


class UserDB(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    full_name: Optional[str]
    phone_number: Optional[int]
    password: Optional[str]
    is_admin: bool
    is_active: bool
    created_at: Optional[str]
