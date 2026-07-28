"""
Hikmah AI — Main Entry Point
Production-ready Telegram AI Platform
"""
from __future__ import annotations

import asyncio
import os
import sys

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

from utils.logger import logger


async def main() -> None:
    logger.info("🚀 Hikmah AI starting...")

    # ── Load Settings ─────────────────────────────
    from config.settings import settings

    # ── Initialize Database ───────────────────────
    try:
        from database.sqlite import init_db
        await init_db()
    except Exception as e:
        logger.critical(f"Database init failed: {e}")
        sys.exit(1)

    # ── Initialize Firebase (optional) ────────────
    from database.firebase import init_firebase
    firebase_ok = init_firebase()
    if firebase_ok:
        logger.info("✅ Firebase connected")
    else:
        logger.warning("⚠️ Firebase not configured — running without Firebase")

    # ── Create Bot & Dispatcher ───────────────────
    from bot.main import create_bot, create_dispatcher
    bot = create_bot()
    dp = create_dispatcher()

    # ── Start Scheduler ───────────────────────────
    try:
        from services.scheduler import start_scheduler
        start_scheduler(bot)
        logger.info("✅ Scheduler started")
    except ImportError:
        logger.warning("Scheduler not configured")

    # ── Bot Info ──────────────────────────────────
    try:
        bot_info = await bot.get_me()
        logger.info(f"🤖 Bot: @{bot_info.username} | ID: {bot_info.id}")
    except Exception as e:
        logger.critical(f"Cannot connect to Telegram: {e}")
        sys.exit(1)

    # ── Start Bot ─────────────────────────────────
    if settings.bot_mode == "webhook" and settings.webhook_host:
        await _start_webhook(bot, dp, settings)
    else:
        await _start_polling(bot, dp)


async def _start_polling(bot, dp) -> None:
    from aiogram.types import BotCommand, BotCommandScopeDefault

    # Set commands
    commands = [
        BotCommand(command="start", description="🏠 Boshlanish"),
        BotCommand(command="help", description="❓ Yordam"),
        BotCommand(command="profile", description="👤 Profil"),
        BotCommand(command="premium", description="💎 Premium"),
        BotCommand(command="promo", description="🎟️ Promo kod"),
        BotCommand(command="admin", description="🛡️ Admin panel"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

    logger.info("📡 Starting polling mode...")
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


async def _start_webhook(bot, dp, settings) -> None:
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    logger.info(f"🌐 Starting webhook mode: {settings.webhook_host}{settings.webhook_path}")

    await bot.set_webhook(
        url=f"{settings.webhook_host}{settings.webhook_path}",
        secret_token=settings.webhook_secret or "",
        drop_pending_updates=True,
    )

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret or "",
    )
    webhook_requests_handler.register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.api_host, settings.api_port)
    await site.start()

    logger.info(f"✅ Webhook running on {settings.api_host}:{settings.api_port}")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Hikmah AI stopped.")
