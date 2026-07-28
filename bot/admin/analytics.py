"""
Hikmah AI — Admin Analytics Handler (Deep stats, charts)
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func, and_

from bot.filters.admin import IsAdmin
from database.models import User, AIUsage
from services.analytics_service import get_full_stats, format_stats
from utils.helpers import format_number

router = Router()
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "adm:analytics")
async def show_analytics(callback: CallbackQuery, session=None):
    if not session:
        return

    stats = await get_full_stats(session)

    # AI usage by provider
    now = datetime.now(tz=timezone.utc)
    week_ago = now - timedelta(days=7)
    ai_result = await session.execute(
        select(AIUsage.provider, func.count(AIUsage.id))
        .where(AIUsage.created_at >= week_ago)
        .group_by(AIUsage.provider)
    )
    ai_by_provider = dict(ai_result.all())

    # Top features used
    feat_result = await session.execute(
        select(AIUsage.feature, func.count(AIUsage.id))
        .where(AIUsage.created_at >= week_ago)
        .group_by(AIUsage.feature)
        .order_by(func.count(AIUsage.id).desc())
        .limit(5)
    )
    top_features = feat_result.all()

    text = (
        f"📈 <b>Chuqur Analitika (7 kun)</b>\n\n"
        f"{format_stats(stats)}\n\n"
        f"🤖 <b>AI Provayder bo'yicha (7 kun):</b>\n"
        + "\n".join(f"  • {p.upper()}: {format_number(c)}" for p, c in ai_by_provider.items())
        + f"\n\n🔥 <b>Eng ko'p ishlatiladigan:</b>\n"
        + "\n".join(f"  • {f}: {format_number(c)}" for f, c in top_features)
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Bugungi", callback_data="adm_stats:today"),
        InlineKeyboardButton(text="📆 Haftalik", callback_data="adm_stats:week"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Admin", callback_data="adm:main"))

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("adm_stats:"))
async def detailed_stats(callback: CallbackQuery, session=None):
    if not session:
        return

    period = callback.data.split(":")[1]
    now = datetime.now(tz=timezone.utc)

    periods = {
        "today": ("Bugun", now.replace(hour=0, minute=0, second=0)),
        "week": ("Bu hafta", now - timedelta(days=7)),
        "month": ("Bu oy", now - timedelta(days=30)),
        "all": ("Jami", datetime(2020, 1, 1, tzinfo=timezone.utc)),
    }
    period_name, since = periods.get(period, periods["today"])

    new_users = (await session.execute(
        select(func.count(User.id)).where(User.created_at >= since)
    )).scalar() or 0

    active_users = (await session.execute(
        select(func.count(User.id)).where(User.last_active >= since)
    )).scalar() or 0

    ai_requests = (await session.execute(
        select(func.count(AIUsage.id)).where(AIUsage.created_at >= since)
    )).scalar() or 0

    successful_ai = (await session.execute(
        select(func.count(AIUsage.id)).where(
            and_(AIUsage.created_at >= since, AIUsage.success == True)
        )
    )).scalar() or 0

    success_rate = int(successful_ai / max(ai_requests, 1) * 100)

    text = (
        f"📊 <b>Statistika — {period_name}</b>\n\n"
        f"👥 Yangi foydalanuvchilar: <b>{format_number(new_users)}</b>\n"
        f"⚡ Faol foydalanuvchilar: <b>{format_number(active_users)}</b>\n\n"
        f"🤖 AI so'rovlar: <b>{format_number(ai_requests)}</b>\n"
        f"✅ Muvaffaqiyatli: <b>{format_number(successful_ai)}</b>\n"
        f"📈 Muvaffaqiyat darajasi: <b>{success_rate}%</b>"
    )

    from bot.keyboards.admin_menu import admin_stats_keyboard
    await callback.message.edit_text(text, reply_markup=admin_stats_keyboard(), parse_mode="HTML")
