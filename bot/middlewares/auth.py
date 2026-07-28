"""
Hikmah AI — Auth & User Registration Middleware
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, Update

from database.sqlite import AsyncSessionLocal
from services.user_service import UserService
from utils.helpers import generate_referral_code
from utils.logger import logger


class AuthMiddleware(BaseMiddleware):
    """
    Ensure every user is registered in the database.
    Injects `user` and `session` into handler data.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_data = None

        # Extract Telegram user from event
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                user_data = event.message.from_user
            elif event.callback_query and event.callback_query.from_user:
                user_data = event.callback_query.from_user

        if not user_data:
            return await handler(event, data)

        async with AsyncSessionLocal() as session:
            try:
                user, is_new = await UserService.get_or_create(
                    session=session,
                    telegram_id=user_data.id,
                    username=user_data.username,
                    full_name=user_data.full_name,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                )

                # Check if banned
                if user.is_banned:
                    if isinstance(event, Update) and event.message:
                        await event.message.answer(
                            "🚫 Siz botdan bloklangansiz. Murojaat: @HikmahSupport"
                        )
                    return

                data["user"] = user
                data["session"] = session
                data["is_new_user"] = is_new

                return await handler(event, data)
            except Exception as e:
                logger.error(f"AuthMiddleware error for {user_data.id}: {e}")
                data["user"] = None
                data["session"] = session
                return await handler(event, data)
