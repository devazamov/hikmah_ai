"""
Hikmah AI — Weather Service (OpenWeatherMap free API)
"""
from __future__ import annotations

from typing import Optional

import aiohttp

from config.settings import settings
from utils.logger import logger

WEATHER_BASE = "https://api.openweathermap.org/data/2.5"
ICONS = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
}


async def get_weather(city: str) -> Optional[str]:
    """Fetch weather for city. Returns formatted string or None."""
    if not settings.weather_api_key:
        return (
            "❌ Ob-havo xizmati sozlanmagan.\n"
            "Admin WEATHER_API_KEY ni .env ga kiriting."
        )

    params = {
        "q": city,
        "appid": settings.weather_api_key,
        "units": "metric",
        "lang": "uz",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{WEATHER_BASE}/weather", params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 404:
                    return f"❌ '{city}' shahri topilmadi."
                if resp.status != 200:
                    return "❌ Ob-havo ma'lumotini olishda xatolik."
                data = await resp.json()

        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        icon = ICONS.get(weather.get("main", ""), "🌡️")

        return (
            f"{icon} <b>Ob-havo — {data.get('name', city)}</b>\n\n"
            f"🌡️ Harorat: <b>{main.get('temp', '?'):.0f}°C</b> "
            f"(his qilinadi: {main.get('feels_like', '?'):.0f}°C)\n"
            f"💧 Namlik: <b>{main.get('humidity', '?')}%</b>\n"
            f"🌬️ Shamol: <b>{wind.get('speed', '?')} m/s</b>\n"
            f"☁️ Holat: <b>{weather.get('description', '?').capitalize()}</b>\n"
            f"👁️ Ko'rinish: <b>{data.get('visibility', 0) // 1000} km</b>"
        )
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        return "❌ Ob-havo ma'lumotini olishda xatolik yuz berdi."
