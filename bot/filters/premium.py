"""
Hikmah AI — Premium Filter
"""
from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsPremium(BaseFilter):
    async def __call__(self, message: Message, user=None) -> bool:
        if user is None:
            return False
        return bool(user.is_premium)
