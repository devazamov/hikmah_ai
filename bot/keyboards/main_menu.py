"""
Hikmah AI — Main Menu Keyboards
"""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_reply_keyboard(is_premium: bool = False) -> ReplyKeyboardMarkup:
    """Main bottom reply keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🤖 AI Chat"),
        KeyboardButton(text="🕌 Islomiy"),
    )
    builder.row(
        KeyboardButton(text="🎬 Kino Bot"),
        KeyboardButton(text="🛠️ Vositalar"),
    )
    builder.row(
        KeyboardButton(text="👤 Profil"),
        KeyboardButton(text="⚙️ Sozlamalar"),
    )
    if is_premium:
        builder.row(KeyboardButton(text="💎 Premium Panel"))
    else:
        builder.row(KeyboardButton(text="💎 Premium Olish"))
    return builder.as_markup(resize_keyboard=True)


def tools_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🌤️ Ob-havo", callback_data="tool:weather"),
        InlineKeyboardButton(text="💱 Valyuta", callback_data="tool:currency"),
    )
    builder.row(
        InlineKeyboardButton(text="🔢 Kalkulyator", callback_data="tool:calc"),
        InlineKeyboardButton(text="📱 QR Kod", callback_data="tool:qr"),
    )
    builder.row(
        InlineKeyboardButton(text="🔗 URL Qisqartir", callback_data="tool:url"),
        InlineKeyboardButton(text="📓 Eslatmalar", callback_data="tool:notes"),
    )
    builder.row(
        InlineKeyboardButton(text="⏰ Taymer", callback_data="tool:reminder"),
        InlineKeyboardButton(text="📰 Yangiliklar", callback_data="tool:news"),
    )
    builder.row(
        InlineKeyboardButton(text="📥 Video Yukla", callback_data="tool:video"),
        InlineKeyboardButton(text="🔄 Fayl O'zgartir", callback_data="tool:convert"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="main:back"))
    return builder.as_markup()


def islamic_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📖 Qur'on Oyati", callback_data="islamic:quran"),
        InlineKeyboardButton(text="🕌 Namoz Vaqtlari", callback_data="islamic:prayer"),
    )
    builder.row(
        InlineKeyboardButton(text="🤲 Dua", callback_data="islamic:dua"),
        InlineKeyboardButton(text="📿 Hadis", callback_data="islamic:hadith"),
    )
    builder.row(
        InlineKeyboardButton(text="🎵 Qori Bot", callback_data="islamic:quran_audio"),
        InlineKeyboardButton(text="📅 Islomiy Takvim", callback_data="islamic:calendar"),
    )
    builder.row(
        InlineKeyboardButton(text="❓ Islomiy Savol", callback_data="islamic:question"),
        InlineKeyboardButton(text="🕋 Qibla", callback_data="islamic:qibla"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="main:back"))
    return builder.as_markup()


def ai_personas_keyboard(current: str = "default") -> InlineKeyboardMarkup:
    personas = [
        ("🤖 Hikmah AI", "default"),
        ("🕌 Islomiy Ustoz", "islamic"),
        ("👨‍⚕️ Tabib", "doctor"),
        ("⚖️ Huquqshunos", "lawyer"),
        ("📚 O'qituvchi", "teacher"),
        ("💻 Dasturchi", "programmer"),
        ("🧠 Psixolog", "psychologist"),
        ("📖 Qori Ustoz", "quran_teacher"),
    ]
    builder = InlineKeyboardBuilder()
    for name, key in personas:
        prefix = "✅ " if key == current else ""
        builder.add(InlineKeyboardButton(
            text=f"{prefix}{name}",
            callback_data=f"persona:{key}"
        ))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="settings:back"))
    return builder.as_markup()


def profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="profile:stats"),
        InlineKeyboardButton(text="🏆 Yutuqlar", callback_data="profile:achievements"),
    )
    builder.row(
        InlineKeyboardButton(text="👥 Referral", callback_data="profile:referral"),
        InlineKeyboardButton(text="📋 Tarix", callback_data="profile:history"),
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Kunlik Bonus", callback_data="profile:daily_bonus"),
    )
    return builder.as_markup()


def subscription_keyboard(channels: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        title = ch.get("title", "Kanal")
        link = ch.get("invite_link") or (
            f"https://t.me/{ch['username']}" if ch.get("username") else None
        )
        if link:
            builder.row(InlineKeyboardButton(text=f"📢 {title}", url=link))
    builder.row(InlineKeyboardButton(text="✅ Tekshirish", callback_data="check:subscription"))
    return builder.as_markup()


def premium_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🥉 Basic — 30 kun", callback_data="premium:basic"),
    )
    builder.row(
        InlineKeyboardButton(text="🥈 Pro — 30 kun", callback_data="premium:pro"),
    )
    builder.row(
        InlineKeyboardButton(text="🥇 Ultra — 30 kun", callback_data="premium:ultra"),
    )
    builder.row(
        InlineKeyboardButton(text="🎟️ Promo Kod", callback_data="premium:promo"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="main:back"))
    return builder.as_markup()


def settings_keyboard(lang: str, notif: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🌐 Til O'zgartir", callback_data="settings:lang"),
        InlineKeyboardButton(text="🤖 AI Model", callback_data="settings:model"),
    )
    builder.row(
        InlineKeyboardButton(text="🎭 AI Persona", callback_data="settings:persona"),
        InlineKeyboardButton(
            text=f"🔔 Bildirishnomalar: {'✅' if notif else '❌'}",
            callback_data="settings:notifications"
        ),
    )
    builder.row(
        InlineKeyboardButton(text="🗑️ Suhbatni Tozala", callback_data="settings:clear_history"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="main:back"))
    return builder.as_markup()


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇸🇦 Arabcha", callback_data="lang:ar"),
    )
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Ruscha", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 Inglizcha", callback_data="lang:en"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="settings:back"))
    return builder.as_markup()


def movie_keyboard(movie_code: str, has_file: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if has_file:
        builder.row(InlineKeyboardButton(text="🎬 Yuklab Olish", callback_data=f"movie:get:{movie_code}"))
    builder.row(
        InlineKeyboardButton(text="🔍 Qidiruv", callback_data="movie:search"),
        InlineKeyboardButton(text="📋 Ro'yxat", callback_data="movie:list"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="main:back"))
    return builder.as_markup()


def leaderboard_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⭐ Balllar", callback_data="lb:points"),
        InlineKeyboardButton(text="🤖 AI So'rovlar", callback_data="lb:requests"),
    )
    builder.row(
        InlineKeyboardButton(text="👥 Referallar", callback_data="lb:referrals"),
        InlineKeyboardButton(text="🔥 Seriya", callback_data="lb:streak"),
    )
    return builder.as_markup()


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def video_quality_keyboard(url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📱 360p", callback_data=f"vdl:360:{url[:50]}"),
        InlineKeyboardButton(text="🎬 720p", callback_data=f"vdl:720:{url[:50]}"),
    )
    builder.row(
        InlineKeyboardButton(text="🎵 Faqat Audio (MP3)", callback_data=f"vdl:audio:{url[:50]}"),
    )
    builder.row(InlineKeyboardButton(text="❌ Bekor", callback_data="vdl:cancel"))
    return builder.as_markup()


def support_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❓ Savol Berish", callback_data="support:question"),
        InlineKeyboardButton(text="🐛 Xato Bildirish", callback_data="support:bug"),
    )
    builder.row(
        InlineKeyboardButton(text="💡 Taklif", callback_data="support:suggestion"),
        InlineKeyboardButton(text="📋 Mening Tiketlarim", callback_data="support:my_tickets"),
    )
    return builder.as_markup()
