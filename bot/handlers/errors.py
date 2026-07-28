"""
Hikmah AI — Global Error Handler
"""
from __future__ import annotations

from aiogram import Router
from aiogram.types import ErrorEvent

from utils.logger import logger

router = Router()


@router.error()
async def global_error_handler(event: ErrorEvent):
    """Catch all unhandled exceptions in handlers."""
    logger.error(
        f"Unhandled error: {event.exception} | "
        f"Update: {event.update.model_dump_json(exclude_none=True)[:300]}"
    )

    # Try to notify user
    try:
        if event.update.message:
            await event.update.message.answer(
                "❌ Kutilmagan xatolik yuz berdi.\n"
                "Iltimos, keyinroq urinib ko'ring yoki /start bosing."
            )
        elif event.update.callback_query:
            await event.update.callback_query.answer(
                "❌ Xatolik! /start bosing.",
                show_alert=True,
            )
    except Exception:
        pass
