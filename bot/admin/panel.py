"""
Hikmah AI — Admin Panel Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func, text

from bot.filters.admin import IsAdmin
from bot.keyboards.admin_menu import (
    admin_main_keyboard, admin_stats_keyboard, admin_broadcast_keyboard,
    admin_user_actions_keyboard, admin_premium_keyboard, admin_ai_keyboard,
    admin_movie_keyboard, admin_promo_keyboard, admin_channels_keyboard,
)
from database.models import User, AIUsage, Movie, Broadcast
from config.settings import settings
from utils.helpers import format_number, utc_now, progress_bar
from utils.logger import logger
from datetime import datetime, timedelta, timezone

router = Router()
router.message.filter(IsAdmin())


@router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.answer(
        "🛡️ <b>Hikmah AI — Admin Panel</b>\n\n"
        f"👤 Admin: {message.from_user.full_name}\n"
        f"⏰ Vaqt: {utc_now().strftime('%d.%m.%Y %H:%M')} UTC\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:main")
async def admin_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛡️ <b>Admin Panel</b>",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:stats")
async def admin_stats(callback: CallbackQuery, session=None):
    if not session:
        return

    now = utc_now()
    today = now.strftime("%Y-%m-%d")
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    # Total users
    total_result = await session.execute(select(func.count()).where(User.telegram_id > 0))
    total_users = total_result.scalar() or 0

    # Active today
    today_result = await session.execute(
        select(func.count()).where(
            User.last_active >= datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0)
        )
    )
    today_users = today_result.scalar() or 0

    # Premium users
    prem_result = await session.execute(select(func.count()).where(User.is_premium == True))
    premium_users = prem_result.scalar() or 0

    # Total AI requests
    ai_result = await session.execute(select(func.sum(User.total_requests)))
    total_ai = ai_result.scalar() or 0

    # Banned users
    ban_result = await session.execute(select(func.count()).where(User.is_banned == True))
    banned = ban_result.scalar() or 0

    text = (
        f"📊 <b>Umumiy Statistika</b>\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"  • Jami: <b>{format_number(total_users)}</b>\n"
        f"  • Bugun faol: <b>{today_users}</b>\n"
        f"  • Premium: <b>{premium_users}</b>\n"
        f"  • Bloklangan: <b>{banned}</b>\n\n"
        f"🤖 <b>AI Statistika:</b>\n"
        f"  • Jami so'rovlar: <b>{format_number(total_ai)}</b>\n\n"
        f"⏰ Yangilangan: {now.strftime('%H:%M:%S')} UTC"
    )

    await callback.message.edit_text(
        text,
        reply_markup=admin_stats_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:users")
async def admin_users(callback: CallbackQuery):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔍 ID bo'yicha qidirish", callback_data="adm_usr:search_id"),
        InlineKeyboardButton(text="🔍 Username", callback_data="adm_usr:search_un"),
    )
    builder.row(
        InlineKeyboardButton(text="💎 Premium foydalanuvchilar", callback_data="adm_usr:list_prem"),
        InlineKeyboardButton(text="🚫 Bloklangan", callback_data="adm_usr:list_banned"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Top 10 (ball)", callback_data="adm_usr:top_points"),
        InlineKeyboardButton(text="📥 Export CSV", callback_data="adm:export"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Admin Panel", callback_data="adm:main"))

    await callback.message.edit_text(
        "👥 <b>Foydalanuvchi Boshqaruvi</b>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:broadcast")
async def admin_broadcast(callback: CallbackQuery):
    await callback.message.edit_text(
        "📢 <b>Broadcast</b>\n\n"
        "Barcha foydalanuvchilarga xabar yuborish turi:",
        reply_markup=admin_broadcast_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:ai_settings")
async def admin_ai_settings(callback: CallbackQuery, session=None):
    current = settings.default_ai_provider
    available = []
    if settings.gemini_api_key:
        available.append("✅ Gemini")
    if settings.groq_api_key:
        available.append("✅ Groq")
    if settings.openrouter_api_key:
        available.append("✅ OpenRouter")

    text = (
        f"🤖 <b>AI Sozlamalar</b>\n\n"
        f"🔌 Mavjud provayderlar:\n"
        + "\n".join(f"  • {a}" for a in available) + "\n\n"
        f"⚡ Hozirgi: <b>{current.upper()}</b>\n"
        f"🧠 Model: <b>{settings.default_ai_model}</b>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=admin_ai_keyboard(current),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_ai:provider:"))
async def set_ai_provider(callback: CallbackQuery):
    provider = callback.data.split(":")[-1]
    # In production, save to Firebase/DB settings
    await callback.answer(
        f"✅ Provider o'zgartirildi: {provider.upper()}\n"
        "⚠️ Restart talab qilinadi!",
        show_alert=True,
    )


@router.callback_query(F.data == "adm:premium")
async def admin_premium(callback: CallbackQuery):
    await callback.message.edit_text(
        "💎 <b>Premium Boshqaruv</b>\n\n"
        "Foydalanuvchiga premium berish uchun avval foydalanuvchi ID sini yuboring.",
        reply_markup=admin_premium_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_prem:"))
async def admin_give_premium(callback: CallbackQuery):
    plan = callback.data.split(":")[1]
    plans = {
        "basic": ("Basic", 30),
        "pro": ("Pro", 30),
        "ultra": ("Ultra", 30),
        "custom": ("Maxsus", None),
    }
    name, days = plans.get(plan, ("?", 30))

    from aiogram.fsm.context import FSMContext
    await callback.message.edit_text(
        f"💎 <b>{name} Premium berish</b>\n\n"
        f"Foydalanuvchi Telegram ID sini yuboring:\n"
        f"(Masalan: <code>123456789</code>)",
        parse_mode="HTML",
    )
    # In real implementation, set FSM state to wait for user ID


@router.callback_query(F.data == "adm:movies")
async def admin_movies(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎬 <b>Kino Boshqaruv</b>",
        reply_markup=admin_movie_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:promo")
async def admin_promo(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎟️ <b>Promo Kodlar</b>",
        reply_markup=admin_promo_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:channels")
async def admin_channels(callback: CallbackQuery):
    required = settings.required_channels_list
    ch_text = "\n".join(f"  • {ch}" for ch in required) if required else "  Hali yo'q"
    sub_status = "✅ Yoqilgan" if settings.subscription_check_enabled else "❌ O'chirilgan"

    await callback.message.edit_text(
        f"📺 <b>Kanal Boshqaruv</b>\n\n"
        f"Majburiy kanallar:\n{ch_text}\n\n"
        f"Obuna tekshiruvi: <b>{sub_status}</b>",
        reply_markup=admin_channels_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:export")
async def admin_export(callback: CallbackQuery, session=None):
    if not session:
        return

    await callback.answer("⏳ Export tayyorlanmoqda...", show_alert=False)

    result = await session.execute(
        select(User).order_by(User.created_at.desc()).limit(1000)
    )
    users = result.scalars().all()

    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Telegram ID", "Username", "Full Name",
        "Premium", "Points", "Total Requests", "Referrals",
        "Banned", "Created At"
    ])
    for u in users:
        writer.writerow([
            u.id, u.telegram_id, u.username, u.full_name,
            u.is_premium, u.points, u.total_requests, u.referral_count,
            u.is_banned, u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else ""
        ])

    csv_data = output.getvalue().encode("utf-8-sig")

    from aiogram.types import BufferedInputFile
    await callback.message.answer_document(
        BufferedInputFile(csv_data, filename=f"users_{utc_now().strftime('%Y%m%d')}.csv"),
        caption=f"📤 Foydalanuvchilar ro'yxati\n👥 Jami: {len(users)} ta",
    )


@router.callback_query(F.data == "adm:logs")
async def admin_logs(callback: CallbackQuery):
    try:
        import os
        log_file = "logs/hikmah_ai.log"
        if not os.path.exists(log_file):
            await callback.answer("📋 Log fayli topilmadi.", show_alert=True)
            return

        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            last_lines = lines[-30:] if len(lines) > 30 else lines
            content = "".join(last_lines)[-3000:]

        from aiogram.types import BufferedInputFile
        await callback.message.answer_document(
            BufferedInputFile(content.encode(), filename="recent_logs.txt"),
            caption="📋 So'nggi 30 ta log yozuvi",
        )
    except Exception as e:
        await callback.answer(f"❌ Log o'qishda xatolik: {e}", show_alert=True)


@router.callback_query(F.data == "adm:api_keys")
async def admin_api_keys(callback: CallbackQuery):
    keys_status = {
        "🔵 Gemini": "✅" if settings.gemini_api_key else "❌",
        "🟢 Groq": "✅" if settings.groq_api_key else "❌",
        "🟠 OpenRouter": "✅" if settings.openrouter_api_key else "❌",
        "🌤️ Weather": "✅" if settings.weather_api_key else "❌",
        "💱 Currency": "✅" if settings.currency_api_key else "❌",
        "📰 News": "✅" if settings.news_api_key else "❌",
    }

    lines = ["🔑 <b>API Kalitlar Holati</b>\n"]
    for name, status in keys_status.items():
        lines.append(f"{status} {name}")

    lines.append("\n⚠️ API kalitlarni o'zgartirish uchun .env faylini tahrirlang.")

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Admin Panel", callback_data="adm:main"))

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
