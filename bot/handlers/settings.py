"""
Hikmah AI — Settings Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from bot.keyboards.main_menu import (
    settings_keyboard, language_keyboard, ai_personas_keyboard,
)
from database.models import User
from utils.logger import logger

router = Router()

AI_MODELS = {
    "gemini": [
        ("gemini-1.5-flash", "⚡ Gemini Flash (Tez)"),
        ("gemini-1.5-pro", "💎 Gemini Pro (Kuchli)"),
        ("gemini-2.0-flash", "🚀 Gemini 2.0 Flash"),
    ],
    "groq": [
        ("llama-3.3-70b-versatile", "🦙 LLaMA 3.3 70B"),
        ("llama-3.1-8b-instant", "⚡ LLaMA 3.1 8B (Tez)"),
        ("mixtral-8x7b-32768", "🎯 Mixtral 8x7B"),
    ],
    "openrouter": [
        ("openai/gpt-4o-mini", "🤖 GPT-4o Mini"),
        ("openai/gpt-4o", "💎 GPT-4o"),
        ("anthropic/claude-3-haiku", "⚡ Claude Haiku"),
        ("meta-llama/llama-3.1-8b-instruct:free", "🆓 LLaMA 3.1 (Bepul)"),
    ],
}


@router.message(F.text == "⚙️ Sozlamalar")
async def show_settings(message: Message, user: User = None):
    if not user:
        return

    lang_map = {"uz": "🇺🇿 O'zbek", "ar": "🇸🇦 Arabcha", "en": "🇬🇧 Inglizcha", "ru": "🇷🇺 Ruscha"}
    notif_map = {True: "✅ Yoqilgan", False: "❌ O'chirilgan"}

    text = (
        f"⚙️ <b>Sozlamalar</b>\n\n"
        f"🌐 Til: <b>{lang_map.get(user.language, user.language)}</b>\n"
        f"🤖 AI Provayder: <b>{user.ai_provider.upper()}</b>\n"
        f"🧠 AI Model: <b>{user.ai_model}</b>\n"
        f"🎭 Persona: <b>{user.ai_persona}</b>\n"
        f"🔔 Bildirishnomalar: <b>{notif_map.get(user.notifications_enabled, '?')}</b>"
    )

    await message.answer(
        text,
        reply_markup=settings_keyboard(user.language, user.notifications_enabled),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "settings:lang")
async def change_language(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌐 <b>Til tanlang:</b>",
        reply_markup=language_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, user: User = None, session=None):
    if not user or not session:
        return
    lang = callback.data.split(":")[1]
    user.language = lang
    await session.commit()

    lang_map = {"uz": "🇺🇿 O'zbek", "ar": "🇸🇦 Arabcha", "en": "🇬🇧 Inglizcha", "ru": "🇷🇺 Ruscha"}
    await callback.answer(f"✅ Til o'zgartirildi: {lang_map.get(lang, lang)}", show_alert=True)
    await show_settings(callback.message, user=user)


@router.callback_query(F.data == "settings:persona")
async def change_persona(callback: CallbackQuery, user: User = None):
    if not user:
        return
    await callback.message.edit_text(
        "🎭 <b>AI Persona tanlang:</b>\n\n"
        "Har bir persona o'ziga xos uslub va bilim sohasiga ega.",
        reply_markup=ai_personas_keyboard(user.ai_persona),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("persona:"))
async def set_persona(callback: CallbackQuery, user: User = None, session=None):
    if not user or not session:
        return
    persona = callback.data.split(":")[1]
    user.ai_persona = persona
    await session.commit()

    from ai.personas.personas import get_persona
    p = get_persona(persona)
    await callback.answer(f"✅ Persona: {p.emoji} {p.name}", show_alert=True)


@router.callback_query(F.data == "settings:model")
async def change_model(callback: CallbackQuery, user: User = None):
    if not user:
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    models = AI_MODELS.get(user.ai_provider, AI_MODELS["gemini"])
    for model_id, model_name in models:
        prefix = "✅ " if model_id == user.ai_model else ""
        builder.row(InlineKeyboardButton(
            text=f"{prefix}{model_name}",
            callback_data=f"setmodel:{model_id[:40]}"
        ))
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="settings:back"))

    await callback.message.edit_text(
        f"🧠 <b>AI Model tanlang</b>\n"
        f"Hozirgi provayder: <b>{user.ai_provider.upper()}</b>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("setmodel:"))
async def set_model(callback: CallbackQuery, user: User = None, session=None):
    if not user or not session:
        return
    model = callback.data[9:]
    user.ai_model = model
    await session.commit()
    await callback.answer(f"✅ Model: {model}", show_alert=True)


@router.callback_query(F.data == "settings:notifications")
async def toggle_notifications(callback: CallbackQuery, user: User = None, session=None):
    if not user or not session:
        return
    user.notifications_enabled = not user.notifications_enabled
    await session.commit()
    status = "✅ Yoqildi" if user.notifications_enabled else "❌ O'chirildi"
    await callback.answer(f"🔔 Bildirishnomalar: {status}", show_alert=True)


@router.callback_query(F.data == "settings:back")
async def settings_back(callback: CallbackQuery, user: User = None):
    await show_settings(callback.message, user=user)
