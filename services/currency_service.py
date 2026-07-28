"""
Hikmah AI — Currency Service (Free Exchange Rate API)
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import aiohttp

from utils.logger import logger

FREE_API = "https://open.er-api.com/v6/latest"


async def get_rates(base: str = "USD") -> Optional[Dict[str, float]]:
    """Fetch exchange rates from free API."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{FREE_API}/{base}", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data.get("rates", {})
    except Exception as e:
        logger.error(f"Currency fetch error: {e}")
        return None


async def convert_currency(amount: float, from_cur: str, to_cur: str) -> Tuple[Optional[float], str]:
    """Convert currency. Returns (result, formatted_text)."""
    rates = await get_rates(from_cur.upper())
    if not rates:
        return None, "❌ Valyuta kursini olishda xatolik."

    to_upper = to_cur.upper()
    if to_upper not in rates:
        return None, f"❌ '{to_cur}' valyuta topilmadi."

    result = amount * rates[to_upper]
    text = (
        f"💱 <b>Valyuta konvertatsiyasi</b>\n\n"
        f"{'='*25}\n"
        f"💵 {amount:,.2f} {from_cur.upper()}\n"
        f"   ↓\n"
        f"💶 <b>{result:,.4f} {to_upper}</b>\n"
        f"{'='*25}\n"
        f"📊 Kurs: 1 {from_cur.upper()} = {rates[to_upper]:.4f} {to_upper}\n"
        f"⏰ Yangilanish: real vaqt"
    )
    return result, text


async def popular_rates() -> str:
    """Get popular currencies against UZS."""
    rates = await get_rates("UZS")
    if not rates:
        return "❌ Valyuta kurslarini olishda xatolik."

    popular = {
        "USD": "🇺🇸 Dollar",
        "EUR": "🇪🇺 Yevro",
        "RUB": "🇷🇺 Rubl",
        "GBP": "🇬🇧 Funt",
        "CNY": "🇨🇳 Yuan",
        "TRY": "🇹🇷 Lira",
        "KZT": "🇰🇿 Tenge",
        "AED": "🇦🇪 Dirham",
        "SAR": "🇸🇦 Riyal",
    }

    lines = ["💱 <b>Valyuta kurslari (UZS)</b>\n"]
    for code, name in popular.items():
        if code in rates:
            rate = 1 / rates[code]  # UZS per 1 foreign
            lines.append(f"{name}: <b>{rate:,.0f} so'm</b>")

    return "\n".join(lines)
