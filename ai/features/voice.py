"""
Hikmah AI — Voice/Audio Transcription (Whisper via Groq)
"""
from __future__ import annotations

import io
import os
import tempfile
from typing import Optional, Tuple

from config.settings import settings
from utils.logger import logger


async def transcribe_voice(audio_data: bytes, language: str = "uz") -> Tuple[Optional[str], Optional[str]]:
    """
    Transcribe audio to text using Groq Whisper (fast & free tier available).
    Returns (text, error_message)
    """
    if not settings.groq_api_key:
        # Fallback: try local whisper
        return await _transcribe_local(audio_data, language)

    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.groq_api_key)

        # Save audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                transcription = await client.audio.transcriptions.create(
                    file=(os.path.basename(tmp_path), f.read(), "audio/ogg"),
                    model="whisper-large-v3",
                    language=None,  # Auto-detect
                    response_format="text",
                )
            return str(transcription), None
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None, f"❌ Ovozni matnga o'girishda xatolik: {str(e)[:150]}"


async def _transcribe_local(audio_data: bytes, language: str) -> Tuple[Optional[str], Optional[str]]:
    """Fallback: local whisper (if installed)."""
    try:
        import whisper
        import numpy as np
        import asyncio

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        def _run():
            model = whisper.load_model("base")
            result = model.transcribe(tmp_path, language=language if language != "uz" else None)
            return result["text"]

        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, _run)
        os.unlink(tmp_path)
        return text, None
    except ImportError:
        return None, "❌ Ovoz tanish xizmati sozlanmagan. GROQ_API_KEY ni o'rnating."
    except Exception as e:
        return None, f"❌ Xatolik: {str(e)[:100]}"
