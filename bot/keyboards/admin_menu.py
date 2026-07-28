"""
Hikmah AI — Admin Panel Keyboards
"""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="adm:stats"),
        InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="adm:users"),
    )
    builder.row(
        InlineKeyboardButton(text="📢 Broadcast", callback_data="adm:broadcast"),
        InlineKeyboardButton(text="🤖 AI Sozlamalari", callback_data="adm:ai_settings"),
    )
    builder.row(
        InlineKeyboardButton(text="📺 Kanallar", callback_data="adm:channels"),
        InlineKeyboardButton(text="🎬 Kino Boshqaruv", callback_data="adm:movies"),
    )
    builder.row(
        InlineKeyboardButton(text="🎟️ Promo Kodlar", callback_data="adm:promo"),
        InlineKeyboardButton(text="💎 Premium Boshqaruv", callback_data="adm:premium"),
    )
    builder.row(
        InlineKeyboardButton(text="📈 Analytics", callback_data="adm:analytics"),
        InlineKeyboardButton(text="🛡️ Moderatsiya", callback_data="adm:moderation"),
    )
    builder.row(
        InlineKeyboardButton(text="🔑 API Kalitlar", callback_data="adm:api_keys"),
        InlineKeyboardButton(text="⚙️ Bot Sozlamalar", callback_data="adm:bot_settings"),
    )
    builder.row(
        InlineKeyboardButton(text="📤 Export", callback_data="adm:export"),
        InlineKeyboardButton(text="📋 Loglar", callback_data="adm:logs"),
    )
    builder.row(
        InlineKeyboardButton(text="🔔 Webhook", callback_data="adm:webhook"),
        InlineKeyboardButton(text="🎫 Tiketlar", callback_data="adm:tickets"),
    )
    return builder.as_markup()


def admin_stats_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📅 Bugun", callback_data="adm_stats:today"),
        InlineKeyboardButton(text="📆 Hafta", callback_data="adm_stats:week"),
    )
    builder.row(
        InlineKeyboardButton(text="🗓️ Oy", callback_data="adm_stats:month"),
        InlineKeyboardButton(text="📊 Jami", callback_data="adm_stats:all"),
    )
    builder.row(
        InlineKeyboardButton(text="🤖 AI Statistika", callback_data="adm_stats:ai"),
        InlineKeyboardButton(text="💎 Premium Statistika", callback_data="adm_stats:premium"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Admin Panel", callback_data="adm:main"))
    return builder.as_markup()


def admin_user_actions_keyboard(telegram_id: int, is_banned: bool, is_premium: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📋 Ma'lumot", callback_data=f"adm_usr:info:{telegram_id}"),
    )
    if is_premium:
        builder.row(
            InlineKeyboardButton(text="💎 Premium Olish", callback_data=f"adm_usr:rem_prem:{telegram_id}"),
        )
    else:
        builder.row(
            InlineKeyboardButton(text="💎 Premium Berish", callback_data=f"adm_usr:add_prem:{telegram_id}"),
        )
    if is_banned:
        builder.row(
            InlineKeyboardButton(text="✅ Unban", callback_data=f"adm_usr:unban:{telegram_id}"),
        )
    else:
        builder.row(
            InlineKeyboardButton(text="🚫 Ban", callback_data=f"adm_usr:ban:{telegram_id}"),
        )
    builder.row(
        InlineKeyboardButton(text="✉️ Xabar Yuborish", callback_data=f"adm_usr:msg:{telegram_id}"),
        InlineKeyboardButton(text="⚠️ Ogohlantirish", callback_data=f"adm_usr:warn:{telegram_id}"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm:users"))
    return builder.as_markup()


def admin_broadcast_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Matn", callback_data="adm_bc:text"),
        InlineKeyboardButton(text="🖼️ Rasm + Matn", callback_data="adm_bc:photo"),
    )
    builder.row(
        InlineKeyboardButton(text="🎥 Video + Matn", callback_data="adm_bc:video"),
        InlineKeyboardButton(text="🔘 Tugmali Xabar", callback_data="adm_bc:button"),
    )
    builder.row(
        InlineKeyboardButton(text="📎 Forward", callback_data="adm_bc:forward"),
        InlineKeyboardButton(text="📅 Rejali Xabar", callback_data="adm_bc:schedule"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Admin Panel", callback_data="adm:main"))
    return builder.as_markup()


def admin_premium_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🥉 Basic (30 kun)", callback_data="adm_prem:basic"),
        InlineKeyboardButton(text="🥈 Pro (30 kun)", callback_data="adm_prem:pro"),
    )
    builder.row(
        InlineKeyboardButton(text="🥇 Ultra (30 kun)", callback_data="adm_prem:ultra"),
        InlineKeyboardButton(text="🎁 Maxsus muddat", callback_data="adm_prem:custom"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm:main"))
    return builder.as_markup()


def admin_ai_keyboard(current_provider: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    providers = [
        ("🔵 Gemini", "gemini"),
        ("🟢 Groq", "groq"),
        ("🟠 OpenRouter", "openrouter"),
    ]
    for name, key in providers:
        prefix = "✅ " if key == current_provider else ""
        builder.add(InlineKeyboardButton(
            text=f"{prefix}{name}",
            callback_data=f"adm_ai:provider:{key}"
        ))
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="📊 AI Statistika", callback_data="adm_ai:stats"),
        InlineKeyboardButton(text="🔑 API Kalitlar", callback_data="adm:api_keys"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm:main"))
    return builder.as_markup()


def admin_movie_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Kino Qo'shish", callback_data="adm_mv:add"),
        InlineKeyboardButton(text="🔍 Qidirish", callback_data="adm_mv:search"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 Barcha Kinolar", callback_data="adm_mv:list"),
        InlineKeyboardButton(text="🗑️ O'chirish", callback_data="adm_mv:delete"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="adm_mv:stats"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm:main"))
    return builder.as_markup()


def admin_promo_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Yaratish", callback_data="adm_promo:create"),
        InlineKeyboardButton(text="📋 Ro'yxat", callback_data="adm_promo:list"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑️ O'chirish", callback_data="adm_promo:delete"),
        InlineKeyboardButton(text="📊 Statistika", callback_data="adm_promo:stats"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm:main"))
    return builder.as_markup()


def confirm_broadcast_keyboard(preview_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Yuborish", callback_data=f"adm_bc:confirm:{preview_id}"),
        InlineKeyboardButton(text="❌ Bekor", callback_data="adm_bc:cancel"),
    )
    return builder.as_markup()


def url_button_keyboard(text: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, url=url)]
    ])


def admin_channels_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Kanal Qo'shish", callback_data="adm_ch:add"),
        InlineKeyboardButton(text="📋 Kanallar Ro'yxati", callback_data="adm_ch:list"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Obuna Tekshiruvi", callback_data="adm_ch:toggle_sub"),
        InlineKeyboardButton(text="📁 Fayl Indeksi", callback_data="adm_ch:index"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm:main"))
    return builder.as_markup()
