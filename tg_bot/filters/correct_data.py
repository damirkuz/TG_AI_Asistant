from typing import Optional

from aiogram.filters import BaseFilter
from aiogram.types import Message
import re
__all__ = ["CorrectPhone", "CorrectOTPCode", "CorrectPassword"]




class CorrectPhone(BaseFilter):
    async def __call__(self, message: Message) -> Optional[dict[str, str]]:
        if message.contact:
            return {'phone': str(message.contact.phone_number)}
        phone_correct_regex = re.compile(r"^\+?7\d{10}$")
        row_message = message.text.replace(" ", "")
        if phone_correct_regex.fullmatch(row_message):
            return {'phone': row_message}
        return None



class CorrectOTPCode(BaseFilter):
    async def __call__(self, message: Message) -> Optional[dict[str, str]]:
        return {'code': str(int(message.text) - 1)} if message.text.isdigit() else False

class CorrectPassword(BaseFilter):
    async def __call__(self, message: Message) -> Optional[dict[str, str]]:
        return {'password': message.text} if len(message.text) > 4 else False
