"""
Hikmah AI — Logging Middleware
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from utils.logger import logger


class LoggingMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Update):
            if event.message:
                m = event.message
                uid = m.from_user.id if m.from_user else "?"
                uname = m.from_user.username if m.from_user else "?"
                text = (m.text or m.caption or f"[{m.content_type}]")[:80]
                logger.debug(f"MSG [{uid} @{uname}]: {text}")
            elif event.callback_query:
                cq = event.callback_query
                uid = cq.from_user.id
                logger.debug(f"CBQ [{uid}]: {cq.data}")

        return await handler(event, data)
