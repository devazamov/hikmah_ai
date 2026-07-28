"""
Hikmah AI — Text-to-Speech (TTS)
Uses gTTS (Google TTS) — free, no API key needed
"""
from __future__ import annotations

import io
import asyncio
from typing import Optional, Tuple


async def text_to_speech(
    text: str,
    lang: str = "uz",
    slow: bool = False,
) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Convert text to speech using gTTS.
    Returns (audio_bytes, error_message)
    
    Supported languages: uz, ar, en, ru, tr...
    """
    try:
        from gtts import gTTS

        # gTTS language codes
        lang_map = {
            "uz": "uz",
            "ar": "ar",
            "en": "en",
            "ru": "ru",
            "tr": "tr",
            "de": "de",
            "fr": "fr",
        }
        tts_lang = lang_map.get(lang, "en")

        loop = asyncio.get_event_loop()

        def _generate():
            tts = gTTS(text=text[:3000], lang=tts_lang, slow=slow)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()

        audio_bytes = await loop.run_in_executor(None, _generate)
        return audio_bytes, None

    except ImportError:
        return None, "❌ TTS xizmati o'rnatilmagan. `pip install gtts` bajaring."
    except Exception as e:
        return None, f"❌ Ovoz yaratishda xatolik: {str(e)[:100]}"


async def quran_audio_url(surah: int, reciter: str = "ar.alafasy") -> str:
    """Get Quran audio URL from alquran.cloud API."""
    return f"https://cdn.islamic.network/quran/audio-surah/128/{reciter}/{surah}.mp3"
