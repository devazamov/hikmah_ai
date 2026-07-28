"""
Hikmah AI — PDF/CSV Export Utility
"""
from __future__ import annotations
import csv
import io
from typing import List
from database.models import User


def export_users_csv(users: List[User]) -> bytes:
    """Export users list to CSV bytes."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Telegram ID", "Username", "Full Name", "Language",
        "Premium", "Premium Type", "Points", "Level", "Streak",
        "Total Requests", "Referrals", "Is Banned",
        "Created At", "Last Active"
    ])
    for u in users:
        writer.writerow([
            u.telegram_id,
            u.username or "",
            u.full_name or "",
            u.language,
            "Ha" if u.is_premium else "Yo'q",
            u.premium_type or "",
            u.points,
            u.level,
            u.streak,
            u.total_requests,
            u.referral_count,
            "Ha" if u.is_banned else "Yo'q",
            u.created_at.strftime("%d.%m.%Y %H:%M") if u.created_at else "",
            u.last_active.strftime("%d.%m.%Y %H:%M") if u.last_active else "",
        ])
    return output.getvalue().encode("utf-8-sig")  # utf-8-sig for Excel compatibility


def export_stats_text(stats: dict) -> str:
    """Export stats as formatted text for broadcast/report."""
    from utils.helpers import format_number
    lines = [
        "📊 Hikmah AI — Statistika Hisoboti",
        "=" * 35,
        f"👥 Jami foydalanuvchilar: {format_number(stats.get('total_users', 0))}",
        f"💎 Premium: {stats.get('premium', 0)}",
        f"⚡ Bugun faol: {stats.get('active_today', 0)}",
        f"🆕 Hafta yangi: {stats.get('new_week', 0)}",
        f"🤖 Jami AI so'rovlar: {format_number(stats.get('total_ai_requests', 0))}",
        f"⭐ Jami ballar: {format_number(stats.get('total_points', 0))}",
        "=" * 35,
    ]
    return "\n".join(lines)
