"""
Hikmah AI — Voice Message & Audio Handler
Converts voice to text, then processes as AI message
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message, Voice, Audio, Document

from ai.features.voice import transcribe_voice
from ai.features.tts import text_to_speech
from ai.features.pdf_rag import extract_pdf_text, store_pdf_context
from database.models import User
from services.user_service import UserService
from services.ai_service import AIService
from utils.helpers import get_limit_text, progress_bar
from utils.logger import logger

router = Router()


@router.message(F.voice)
async def handle_voice(message: Message, user: User = None, session=None):
    """Voice message → Transcribe → AI reply."""
    if not user or not session:
        return

    # Check limit
    can_use, used, total = await UserService.check_limit(session, user)
    if not can_use:
        await message.answer(
            f"❌ <b>AI limiti tugadi!</b>\n<code>{progress_bar(used, total)}</code>",
            parse_mode="HTML",
        )
        return

    processing = await message.answer("🎙️ <b>Ovoz matnga o'girilmoqda...</b>", parse_mode="HTML")

    # Download voice
    try:
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        voice_bytes = await message.bot.download_file(file.file_path)
        audio_data = voice_bytes.read()
    except Exception as e:
        await processing.edit_text("❌ Ovoz faylni yuklab olishda xatolik.")
        return

    # Transcribe
    text, error = await transcribe_voice(audio_data, user.language)
    if error or not text:
        await processing.edit_text(error or "❌ Ovozni matnga o'girib bo'lmadi.")
        return

    await processing.edit_text(
        f"✅ <b>Siz dedingiz:</b>\n<i>{text[:300]}</i>\n\n🤔 Javob tayyorlanmoqda...",
        parse_mode="HTML",
    )

    # Process as AI message
    response = await AIService.chat(session=session, user=user, user_message=text)
    await UserService.increment_usage(session, user)

    await processing.delete()

    if response.success:
        await message.answer(
            f"🎙️ <b>Siz:</b> <i>{text[:200]}</i>\n\n"
            f"🤖 <b>Javob:</b>\n{response.text}",
            parse_mode="HTML",
        )
    else:
        await message.answer(f"❌ {response.error}")


@router.message(F.audio)
async def handle_audio(message: Message, user: User = None, session=None):
    """Audio file → Transcribe."""
    processing = await message.answer("🎵 <b>Audio fayl tahlil qilinmoqda...</b>", parse_mode="HTML")

    try:
        file = await message.bot.get_file(message.audio.file_id)
        audio_bytes = await message.bot.download_file(file.file_path)
        audio_data = audio_bytes.read()
    except Exception:
        await processing.edit_text("❌ Audio yuklab olishda xatolik.")
        return

    text, error = await transcribe_voice(audio_data)
    await processing.delete()

    if error:
        await message.answer(error)
    else:
        await message.answer(
            f"📝 <b>Audiodagi matn:</b>\n\n{text}",
            parse_mode="HTML",
        )


@router.message(F.document.mime_type == "application/pdf")
async def handle_pdf(message: Message, user: User = None, session=None):
    """PDF document → Store context for RAG chat."""
    if not user:
        return

    processing = await message.answer("📄 <b>PDF yuklanmoqda...</b>", parse_mode="HTML")

    try:
        file = await message.bot.get_file(message.document.file_id)
        pdf_bytes = await message.bot.download_file(file.file_path)
        pdf_data = pdf_bytes.read()
    except Exception:
        await processing.edit_text("❌ PDF yuklab olishda xatolik.")
        return

    text = await extract_pdf_text(pdf_data)

    if not text:
        await processing.edit_text("❌ PDF dan matn ajratib bo'lmadi (scan yoki himoyalangan bo'lishi mumkin).")
        return

    store_pdf_context(user.telegram_id, text)
    word_count = len(text.split())

    await processing.edit_text(
        f"✅ <b>PDF muvaffaqiyatli yuklandi!</b>\n\n"
        f"📄 Fayl: {message.document.file_name or 'document.pdf'}\n"
        f"📊 So'zlar: ~{word_count:,}\n\n"
        f"💬 Endi PDF haqida savol bering!\n"
        f"Masalan: <i>'Ushbu hujjatning asosiy fikri nima?'</i>",
        parse_mode="HTML",
    )
