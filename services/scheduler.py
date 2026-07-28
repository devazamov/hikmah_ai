"""
Hikmah AI — APScheduler (Background Jobs)
- Daily limit reset
- Premium expiry check
- Reminder notifications
- Inactive user re-engagement
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from utils.logger import logger

scheduler = AsyncIOScheduler(timezone="UTC")


def start_scheduler(bot) -> None:
    # Every day at 00:00 UTC — reset daily limits
    scheduler.add_job(
        reset_daily_limits,
        CronTrigger(hour=0, minute=0),
        id="daily_reset",
        replace_existing=True,
    )

    # Every hour — check premium expiry
    scheduler.add_job(
        check_premium_expiry,
        IntervalTrigger(hours=1),
        id="premium_check",
        replace_existing=True,
    )

    # Every 5 minutes — send reminders
    scheduler.add_job(
        send_reminders,
        IntervalTrigger(minutes=5),
        args=[bot],
        id="reminders",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("✅ Scheduler started with jobs: daily_reset, premium_check, reminders")


async def reset_daily_limits() -> None:
    """Reset all users' daily AI request counters."""
    from database.sqlite import AsyncSessionLocal
    from database.models import User
    from sqlalchemy import update

    async with AsyncSessionLocal() as session:
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        await session.execute(
            update(User).where(User.daily_reset_date != today).values(
                daily_requests_used=0,
                daily_reset_date=today,
            )
        )
        await session.commit()
    logger.info("✅ Daily AI limits reset.")


async def check_premium_expiry() -> None:
    """Remove expired premium subscriptions."""
    from database.sqlite import AsyncSessionLocal
    from database.models import User
    from sqlalchemy import select

    now = datetime.now(tz=timezone.utc)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.is_premium == True,
                User.premium_expires != None,
                User.premium_expires < now,
            )
        )
        expired = result.scalars().all()
        for user in expired:
            user.is_premium = False
            user.premium_type = None
            logger.info(f"Premium expired for user {user.telegram_id}")
        if expired:
            await session.commit()
            logger.info(f"✅ {len(expired)} premium subscriptions expired.")


async def send_reminders(bot) -> None:
    """Send due reminders to users."""
    from database.sqlite import AsyncSessionLocal
    from database.models import Reminder
    from sqlalchemy import select

    now = datetime.now(tz=timezone.utc)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Reminder).where(
                Reminder.is_sent == False,
                Reminder.remind_at <= now,
            )
        )
        reminders = result.scalars().all()

        for reminder in reminders:
            try:
                await bot.send_message(
                    reminder.telegram_id,
                    f"⏰ <b>Eslatma!</b>\n\n{reminder.text}",
                    parse_mode="HTML",
                )
                reminder.is_sent = True
            except Exception as e:
                logger.warning(f"Cannot send reminder to {reminder.telegram_id}: {e}")

        if reminders:
            await session.commit()
