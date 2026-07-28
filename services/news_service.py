"""
Hikmah AI — News Service (newsapi.org free API)
"""
from __future__ import annotations
from typing import List, Optional
import aiohttp
from config.settings import settings
from utils.logger import logger


async def get_news(query: str = "Uzbekistan", lang: str = "uz") -> str:
    """Fetch top news headlines."""
    if not settings.news_api_key:
        # Fallback: use free RSS
        return await _get_rss_news()

    try:
        params = {
            "q": query,
            "apiKey": settings.news_api_key,
            "language": "ru",  # NewsAPI doesn't support Uzbek yet
            "pageSize": 5,
            "sortBy": "publishedAt",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://newsapi.org/v2/everything",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    return await _get_rss_news()
                data = await resp.json()

        articles = data.get("articles", [])[:5]
        if not articles:
            return "❌ Yangiliklar topilmadi."

        lines = [f"📰 <b>Yangiliklar — {query}</b>\n"]
        for i, art in enumerate(articles, 1):
            title = art.get("title", "?")[:100]
            url = art.get("url", "")
            source = art.get("source", {}).get("name", "?")
            lines.append(f"{i}. <a href='{url}'>{title}</a>\n   📡 {source}")

        return "\n\n".join(lines)
    except Exception as e:
        logger.error(f"News fetch error: {e}")
        return await _get_rss_news()


async def _get_rss_news() -> str:
    """Fallback: O'zbekiston yangiliklari (kun.uz RSS)."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://kun.uz/rss",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    return "❌ Yangiliklar mavjud emas. Keyinroq urinib ko'ring."
                text = await resp.text()

        import re
        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", text)[1:6]
        links = re.findall(r"<link>(https://kun\.uz[^<]+)</link>", text)[:5]

        if not titles:
            return "❌ Yangiliklar mavjud emas."

        lines = ["📰 <b>Kun.uz — So'nggi yangiliklar</b>\n"]
        for i, (t, l) in enumerate(zip(titles, links), 1):
            lines.append(f"{i}. <a href='{l}'>{t[:100]}</a>")

        return "\n\n".join(lines)
    except Exception as e:
        logger.error(f"RSS news error: {e}")
        return "❌ Yangiliklar mavjud emas. Keyinroq urinib ko'ring."
