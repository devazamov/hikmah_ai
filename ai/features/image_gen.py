"""
Hikmah AI — AI Image Generation
Supports: OpenAI DALL-E, Stability AI, Pollinations (free)
"""
from __future__ import annotations

import asyncio
import io
from typing import Optional, Tuple

import aiohttp

from config.settings import settings
from utils.logger import logger


async def generate_image_pollinations(prompt: str, width: int = 1024, height: int = 1024) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Free AI image generation via Pollinations.ai (no API key needed).
    Returns (image_bytes, error_message)
    """
    import urllib.parse
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status != 200:
                    return None, "❌ Rasm yaratishda xatolik yuz berdi."
                data = await resp.read()
                return data, None
    except asyncio.TimeoutError:
        return None, "❌ Rasm yaratish vaqti tugadi (60 soniya). Qaytadan urinib ko'ring."
    except Exception as e:
        logger.error(f"Image gen error (pollinations): {e}")
        return None, f"❌ Xatolik: {str(e)[:100]}"


async def generate_image_openai(prompt: str, size: str = "1024x1024") -> Tuple[Optional[bytes], Optional[str]]:
    """Generate image using OpenAI DALL-E (requires API key)."""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openrouter_api_key or "")
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        async with aiohttp.ClientSession() as s:
            async with s.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                data = await r.read()
                return data, None
    except Exception as e:
        logger.error(f"DALL-E error: {e}")
        return None, f"❌ DALL-E xatosi: {str(e)[:150]}"


async def generate_image(
    prompt: str,
    style: str = "realistic",
    width: int = 1024,
    height: int = 1024,
) -> Tuple[Optional[bytes], Optional[str]]:
    """Main image generation dispatcher."""
    # Add style prefix to prompt
    style_prefixes = {
        "realistic": "photorealistic, high quality, detailed",
        "anime": "anime style, high quality, vibrant colors",
        "cartoon": "cartoon style, colorful, fun",
        "oil_painting": "oil painting, artistic, classical style",
        "watercolor": "watercolor painting, soft colors, artistic",
        "digital_art": "digital art, concept art, high quality",
        "islamic": "islamic geometric art, arabesque pattern, beautiful",
        "minimalist": "minimalist, clean, simple design",
    }
    prefix = style_prefixes.get(style, "high quality, detailed")
    full_prompt = f"{prefix}: {prompt}"

    # Try Pollinations first (always free)
    image_bytes, error = await generate_image_pollinations(full_prompt, width, height)
    return image_bytes, error
