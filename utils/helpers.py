"""
Hikmah AI — Helper Utilities
"""
from __future__ import annotations

import hashlib
import random
import string
from datetime import datetime, timezone
from typing import Optional


def generate_referral_code(user_id: int) -> str:
    """Generate unique referral code from user ID."""
    base = f"{user_id}{random.randint(1000, 9999)}"
    return hashlib.md5(base.encode()).hexdigest()[:8].upper()


def generate_promo_code(length: int = 10) -> str:
    """Generate random promo code."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def progress_bar(current: int, total: int, length: int = 10) -> str:
    """
    Generate Telegram-style progress bar.
    Example: ██████░░░░ 30/50
    """
    filled = int(length * current / max(total, 1))
    empty = length - filled
    bar = "█" * filled + "░" * empty
    return f"{bar} {current}/{total}"


def format_number(n: int | float) -> str:
    """Format large numbers with commas: 1000000 → 1,000,000"""
    return f"{n:,}"


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def truncate(text: str, max_len: int = 200) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text


def escape_md(text: str) -> str:
    """Escape Markdown v2 special chars."""
    chars = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in chars else c for c in text)


def get_greeting(name: Optional[str] = None) -> str:
    """Return a random warm Islamic greeting."""
    greetings = [
        f"Assalomu alaykum{',' + name if name else ''}! 👋 Hikmah AI ga xush kelibsiz.",
        f"Va alaykum assalom{',' + name if name else ''}! 🌟 Bugun sizga qanday yordam bera olaman?",
        f"Xush kelibsiz{',' + name if name else ''}! 🤖 Men Hikmah AI — bilim va hikmat yordamchingiz.",
        f"Salom{',' + name if name else ''}! ✨ Yana ko'rishganimizdan xursandman.",
        "Bismillahir rahmanir rahim! 🕌 Hikmah AI xizmatida.",
        f"Ahlan wa sahlan{',' + name if name else ''}! 🌙 Savolingiz nima?",
    ]
    return random.choice(greetings)


def get_limit_text(used: int, total: int) -> str:
    """Return formatted limit status."""
    bar = progress_bar(used, total)
    percent = int(used / max(total, 1) * 100)
    if percent >= 100:
        return (
            f"❌ <b>Bugungi limit tugadi!</b>\n"
            f"<code>{bar}</code>\n"
            "⏰ Limit ertaga avtomatik tiklanadi."
        )
    elif percent >= 80:
        return (
            f"⚠️ <b>AI limiti (qolgan:</b> {total - used}<b>)</b>\n"
            f"<code>{bar}</code>"
        )
    else:
        return (
            f"🤖 <b>AI limiti:</b>\n"
            f"<code>{bar}</code>"
        )


def level_info(points: int) -> dict:
    """Return level info based on points."""
    levels = [
        {"name": "🌱 Yangi boshlovchi", "min": 0,      "max": 99},
        {"name": "📚 O'quvchi",          "min": 100,    "max": 499},
        {"name": "🎓 Bilimdon",          "min": 500,    "max": 1499},
        {"name": "🌟 Ustoz",             "min": 1500,   "max": 3999},
        {"name": "🔥 Ekspert",           "min": 4000,   "max": 9999},
        {"name": "💎 Grand Master",      "min": 10000,  "max": 999999},
    ]
    for lvl in levels:
        if lvl["min"] <= points <= lvl["max"]:
            nxt = lvl["max"] + 1
            progress = progress_bar(points - lvl["min"], lvl["max"] - lvl["min"] + 1)
            return {**lvl, "points": points, "next": nxt, "progress": progress}
    return levels[-1]


def islamic_greeting() -> str:
    """Random Islamic greeting."""
    opts = [
        "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ 🕌",
        "السَّلَامُ عَلَيْكُمْ وَرَحْمَةُ اللَّهِ وَبَرَكَاتُهُ 🌙",
        "الحمد لله رب العالمين ✨",
        "اللهم صل على محمد 🌹",
    ]
    return random.choice(opts)
