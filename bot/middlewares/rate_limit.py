"""
Hikmah AI — Rate Limit & Flood Protection Middleware
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, Update

from utils.security import flood_protection, rate_limiter
from utils.logger import logger


class RateLimitMiddleware(BaseMiddleware):
    """Block users who send too many messages (flood protection)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None
        msg = None

        if isinstance(event, Update):
            if event.message and event.message.from_user:
                user_id = event.message.from_user.id
                msg = event.message

        if not user_id:
            return await handler(event, data)

        # Flood check (per second)
        if flood_protection.is_flood(user_id):
            logger.warning(f"Flood detected from {user_id}")
            return  # Silently ignore

        # Rate limit check (per minute)
        allowed, retry_after = rate_limiter.is_allowed(user_id)
        if not allowed:
            if msg:
                await msg.answer(
                    f"⚠️ Juda tez xabar yuboryapsiz!\n"
                    f"⏳ <b>{retry_after}</b> soniyadan keyin urinib ko'ring.",
                    parse_mode="HTML",
                )
            return

        return await handler(event, data)
