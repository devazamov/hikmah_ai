"""
Hikmah AI — Vision Handler (AI sees and analyzes images)
Supports: Google Gemini Vision, OpenRouter Vision models
Only activates when photo has a caption (question about the image).
"""
from __future__ import annotations

import base64
from typing import Optional

from aiogram import F, Router
from aiogram.types import Message

from ai import ai_manager
from ai.base import Message as AIMsg, AIResponse
from database.models import User
from services.user_service import UserService
from utils.helpers import progress_bar
from utils.logger import logger

router = Router()


async def analyze_image(image_data: bytes, prompt: str) -> AIResponse:
    """Analyze image using multimodal AI."""
    b64 = base64.b64encode(image_data).decode()

    # Try Gemini Vision first (best free option)
    if ai_manager.gemini:
        try:
            import google.generativeai as genai
            import PIL.Image
            import io as _io
            from config.settings import settings
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            img = PIL.Image.open(_io.BytesIO(image_data))
            response = await model.generate_content_async([prompt, img])
            return AIResponse(
                text=response.text,
                provider="gemini",
                model="gemini-1.5-flash-vision",
                success=True,
            )
        except Exception as e:
            logger.warning(f"Gemini Vision failed: {e}")

    # Fallback: OpenRouter Vision (gpt-4o-mini)
    if ai_manager.openrouter:
        try:
            from openai import AsyncOpenAI
            from config.settings import settings
            client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.openrouter_api_key,
            )
            resp = await client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                }],
                max_tokens=1000,
            )
            return AIResponse(
                text=resp.choices[0].message.content,
                provider="openrouter",
                model="gpt-4o-mini-vision",
                success=True,
            )
        except Exception as e:
            logger.warning(f"OpenRouter Vision failed: {e}")

    return AIResponse(
        text=(
            "❌ Vision xizmati sozlanmagan.\n"
            "Gemini yoki OpenRouter API kalitini .env ga kiriting."
        ),
        provider="none",
        model="none",
        success=False,
    )


# Only fire when photo has a caption (user asking something about the image)
@router.message(F.photo & F.caption)
async def handle_photo_vision(message: Message, user: User = None, session=None):
    """AI Vision: analyze photo with caption."""
    if not user or not session:
        return

    can_use, used, total = await UserService.check_limit(session, user)
    if not can_use:
        await message.answer(
            f"❌ AI limiti tugadi!\n<code>{progress_bar(used, total)}</code>",
            parse_mode="HTML",
        )
        return

    prompt = message.caption or "Bu rasmni tahlil qil. O'zbek tilida javob ber."
    processing = await message.answer(
        "👁️ <b>Rasm tahlil qilinmoqda...</b>", parse_mode="HTML"
    )

    try:
        file = await message.bot.get_file(message.photo[-1].file_id)
        photo_buf = await message.bot.download_file(file.file_path)
        image_data = photo_buf.read()
    except Exception:
        await processing.edit_text("❌ Rasm yuklab olishda xatolik.")
        return

    response = await analyze_image(image_data, prompt)
    await processing.delete()

    if response.success:
        await UserService.increment_usage(session, user)
        await message.answer(
            f"👁️ <b>AI Vision:</b>\n\n{response.text}",
            parse_mode="HTML",
        )
    else:
        await message.answer(response.text)
