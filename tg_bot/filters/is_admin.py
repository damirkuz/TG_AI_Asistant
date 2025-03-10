from aiogram.filters import BaseFilter
from aiogram.types import Message
__all__ = ["IsAdmin"]


class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: set[int]) -> None:
        self.admin_ids = admin_ids

    def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids
