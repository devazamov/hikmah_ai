"""
Hikmah AI — Bot Setup & Router Registration (v2 — Full Features)
"""
from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.middlewares import AuthMiddleware, RateLimitMiddleware, LoggingMiddleware
from bot.handlers import (
    start, ai_chat, profile, settings, islamic, tools,
    movies, premium, errors, help, support,
    voice_handler, image_handler, translator_handler, tts_handler,
    sticker_poll, games, quran_audio, channel_files, reminders_handler,
    feedback, vision_handler,
)
from bot.admin import panel, broadcast, movies_admin, users_admin, promo_admin, analytics
from config.settings import settings as app_settings
from utils.logger import logger


def create_bot() -> Bot:
    return Bot(
        token=app_settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # ── Middlewares ────────────────────────────────
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(RateLimitMiddleware())
    dp.update.middleware(AuthMiddleware())

    # ── Error Handler (first) ──────────────────────
    dp.include_router(errors.router)

    # ── Admin Routers ──────────────────────────────
    dp.include_router(panel.router)
    dp.include_router(broadcast.router)
    dp.include_router(movies_admin.router)
    dp.include_router(users_admin.router)
    dp.include_router(promo_admin.router)
    dp.include_router(analytics.router)

    # ── User / Feature Routers ─────────────────────
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(profile.router)
    dp.include_router(settings.router)
    dp.include_router(premium.router)
    dp.include_router(feedback.router)

    # ── Islamic & Quran ────────────────────────────
    dp.include_router(islamic.router)
    dp.include_router(quran_audio.router)

    # ── Tools ──────────────────────────────────────
    dp.include_router(tools.router)
    dp.include_router(reminders_handler.router)
    dp.include_router(sticker_poll.router)
    dp.include_router(games.router)

    # ── Content ────────────────────────────────────
    dp.include_router(movies.router)
    dp.include_router(channel_files.router)
    dp.include_router(support.router)

    # ── AI Feature Routers ─────────────────────────
    dp.include_router(image_handler.router)
    dp.include_router(translator_handler.router)
    dp.include_router(tts_handler.router)

    # ── Media Handlers (before main chat) ──────────
    # vision_handler catches F.photo with caption only
    dp.include_router(vision_handler.router)
    # voice_handler catches F.voice, F.audio, F.document(pdf)
    dp.include_router(voice_handler.router)

    # ── Main AI Chat (LAST — catches all remaining text) ──
    dp.include_router(ai_chat.router)

    logger.info("✅ Dispatcher configured — all routers registered")
    return dp
