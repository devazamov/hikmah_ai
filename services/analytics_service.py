"""
Hikmah AI — Analytics Service
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from sqlalchemy import select, func
from database.models import User, AIUsage
from utils.helpers import format_number


async def get_full_stats(session) -> Dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
    active_today = (await session.execute(
        select(func.count(User.id)).where(User.last_active >= today_start)
    )).scalar() or 0
    new_this_week = (await session.execute(
        select(func.count(User.id)).where(User.created_at >= week_ago)
    )).scalar() or 0
    new_this_month = (await session.execute(
        select(func.count(User.id)).where(User.created_at >= month_ago)
    )).scalar() or 0
    premium_count = (await session.execute(
        select(func.count(User.id)).where(User.is_premium == True)
    )).scalar() or 0
    banned_count = (await session.execute(
        select(func.count(User.id)).where(User.is_banned == True)
    )).scalar() or 0
    total_ai = (await session.execute(select(func.sum(User.total_requests)))).scalar() or 0
    total_points = (await session.execute(select(func.sum(User.points)))).scalar() or 0

    return {
        "total_users": total_users,
        "active_today": active_today,
        "new_week": new_this_week,
        "new_month": new_this_month,
        "premium": premium_count,
        "banned": banned_count,
        "total_ai_requests": total_ai,
        "total_points": total_points,
    }


def format_stats(stats: Dict[str, Any]) -> str:
    return (
        f"📊 <b>To'liq Statistika</b>\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"  • Jami: <b>{format_number(stats['total_users'])}</b>\n"
        f"  • Bugun faol: <b>{stats['active_today']}</b>\n"
        f"  • Hafta yangi: <b>{stats['new_week']}</b>\n"
        f"  • Oy yangi: <b>{stats['new_month']}</b>\n"
        f"  • Premium: <b>{stats['premium']}</b>\n"
        f"  • Ban: <b>{stats['banned']}</b>\n\n"
        f"🤖 <b>AI Statistika:</b>\n"
        f"  • Jami so'rovlar: <b>{format_number(stats['total_ai_requests'])}</b>\n\n"
        f"⭐ <b>Gamifikatsiya:</b>\n"
        f"  • Jami ball: <b>{format_number(stats['total_points'])}</b>"
    )
