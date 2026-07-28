"""
Hikmah AI — Poll Creator Service
"""
from __future__ import annotations

from aiogram import Bot
from aiogram.types import Message


async def create_ai_poll(
    bot: Bot,
    chat_id: int,
    question: str,
    options: list[str],
    is_anonymous: bool = True,
    allows_multiple_answers: bool = False,
) -> bool:
    """Create a Telegram poll."""
    try:
        # Telegram limits: question ≤ 300 chars, 2-10 options, each ≤ 100 chars
        question = question[:300]
        options = [o[:100] for o in options[:10]]
        if len(options) < 2:
            options.append("Boshqa")

        await bot.send_poll(
            chat_id=chat_id,
            question=question,
            options=options,
            is_anonymous=is_anonymous,
            allows_multiple_answers=allows_multiple_answers,
        )
        return True
    except Exception:
        return False


async def create_quiz(
    bot: Bot,
    chat_id: int,
    question: str,
    options: list[str],
    correct_option_id: int = 0,
    explanation: str = "",
) -> bool:
    """Create a Telegram quiz poll."""
    try:
        question = question[:300]
        options = [o[:100] for o in options[:10]]
        if len(options) < 2:
            return False

        await bot.send_poll(
            chat_id=chat_id,
            question=question,
            options=options,
            type="quiz",
            correct_option_id=correct_option_id,
            explanation=explanation[:200] if explanation else None,
            is_anonymous=True,
        )
        return True
    except Exception:
        return False
