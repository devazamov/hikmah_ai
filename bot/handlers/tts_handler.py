"""
Hikmah AI — Text-to-Speech Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from ai.features.tts import text_to_speech
from database.models import User
from services.user_service import UserService

router = Router()


def tts_lang_keyboard() -> any:
    builder = InlineKeyboardBuilder()
    langs = [
        ("🇺🇿 O'zbek", "uz"),
        ("🇸🇦 Arabcha", "ar"),
        ("🇬🇧 Inglizcha", "en"),
        ("🇷🇺 Ruscha", "ru"),
        ("🇹🇷 Turkcha", "tr"),
    ]
    for name, code in langs:
        builder.add(InlineKeyboardButton(text=name, callback_data=f"tts:{code}"))
    builder.adjust(2)
    return builder.as_markup()


@router.message(F.text == "🔊 Matn → Ovoz")
async def tts_start(message: Message):
    await message.answer(
        "🔊 <b>Matn → Ovoz (TTS)</b>\n\n"
        "Avval tilni tanlang:",
        reply_markup=tts_lang_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("tts:") & ~F.data.startswith("tts:send:"))
async def tts_select_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await callback.message.edit_text(
        f"✅ Til tanlandi.\n\n"
        f"📝 Ovozga aylantirmoqchi bo'lgan matnni yuboring (max 500 belgi):",
        parse_mode="HTML",
    )
    await state.update_data(tts_lang=lang)
    from bot.states import AIStates
    await state.set_state(AIStates.waiting_message)


async def send_tts(message: Message, text: str, lang: str = "uz", user: User = None, session=None):
    """Generate and send TTS audio."""
    if not user or not session:
        return

    can_use, used, total = await UserService.check_limit(session, user)
    if not can_use:
        await message.answer("❌ AI limiti tugadi!")
        return

    processing = await message.answer("🔊 Ovoz yaratilmoqda...")
    audio_bytes, error = await text_to_speech(text, lang=lang)

    await processing.delete()

    if error:
        await message.answer(error)
        return

    await message.answer_voice(
        BufferedInputFile(audio_bytes, filename="speech.mp3"),
        caption=f"🔊 <b>Hikmah AI TTS</b>\n<i>{text[:100]}</i>",
        parse_mode="HTML",
    )
    await UserService.increment_usage(session, user)
