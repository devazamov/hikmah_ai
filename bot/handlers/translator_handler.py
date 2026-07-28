"""
Hikmah AI — Translator Handler (AI-powered multi-language translation)
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from bot.states import AIStates
from services.ai_service import AIService
from services.user_service import UserService
from database.models import User
from utils.helpers import progress_bar

router = Router()

LANGUAGES = [
    ("🇺🇿 O'zbek", "uz"),
    ("🇸🇦 Arabcha", "ar"),
    ("🇬🇧 Inglizcha", "en"),
    ("🇷🇺 Ruscha", "ru"),
    ("🇹🇷 Turk", "tr"),
    ("🇩🇪 Nemis", "de"),
    ("🇫🇷 Fransuz", "fr"),
    ("🇨🇳 Xitoy", "zh"),
    ("🇯🇵 Yapon", "ja"),
    ("🇰🇷 Koreys", "ko"),
    ("🇪🇸 Ispan", "es"),
    ("🇮🇳 Hind", "hi"),
]


def translate_target_keyboard() -> any:
    builder = InlineKeyboardBuilder()
    for name, code in LANGUAGES:
        builder.add(InlineKeyboardButton(text=name, callback_data=f"trlang:{code}"))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="❌ Bekor", callback_data="tr:cancel"))
    return builder.as_markup()


@router.message(F.text == "🌐 Tarjimon")
async def translator_start(message: Message, state: FSMContext):
    await message.answer(
        "🌐 <b>AI Tarjimon</b>\n\n"
        "Tarjima qilmoqchi bo'lgan matnni yuboring:",
        parse_mode="HTML",
    )
    await state.set_state(AIStates.waiting_translate)


@router.message(AIStates.waiting_translate)
async def get_translate_text(message: Message, state: FSMContext):
    await state.update_data(translate_text=message.text.strip())
    await message.answer(
        "🌐 <b>Tarjima tilin tanlang:</b>",
        reply_markup=translate_target_keyboard(),
        parse_mode="HTML",
    )
    await state.clear()


@router.callback_query(F.data.startswith("trlang:"))
async def do_translate(callback: CallbackQuery, state: FSMContext, user: User = None, session=None):
    lang = callback.data.split(":")[1]
    data = await state.get_data()
    text = data.get("translate_text", "")

    if not text:
        await callback.answer("❌ Matn topilmadi. Qaytadan bosing.", show_alert=True)
        return

    lang_names = dict(LANGUAGES)
    await callback.message.edit_text(
        f"⏳ <b>{lang_names.get(lang, lang)} tiliga tarjima qilinmoqda...</b>",
        parse_mode="HTML",
    )

    if user and session:
        can_use, used, total = await UserService.check_limit(session, user)
        if not can_use:
            await callback.message.edit_text("❌ AI limiti tugadi! /premium")
            return

    response = await AIService.translate(text, target_lang=lang)

    if user and session:
        await UserService.increment_usage(session, user)

    if response.success:
        await callback.message.edit_text(
            f"🌐 <b>Tarjima ({lang_names.get(lang, lang)}):</b>\n\n{response.text}",
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(f"❌ Tarjimada xatolik: {response.error}")


@router.callback_query(F.data == "tr:cancel")
async def cancel_translate(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Tarjima bekor qilindi.")
