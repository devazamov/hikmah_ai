"""
Hikmah AI — Profile Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func

from bot.keyboards.main_menu import profile_keyboard, leaderboard_keyboard
from database.models import User, Achievement
from services.user_service import UserService
from utils.helpers import progress_bar, level_info, format_number, utc_now
from utils.logger import logger

router = Router()

ACHIEVEMENT_INFO = {
    "first_message": ("🎯", "Birinchi Qadam", "Birinchi AI so'rov"),
    "power_user": ("⚡", "Kuchli Foydalanuvchi", "100 ta AI so'rov"),
    "ai_master": ("🏆", "AI Master", "1000 ta AI so'rov"),
    "streak_7": ("🔥", "Haftachilik", "7 kunlik seriya"),
    "streak_30": ("🌟", "Oylik Chempion", "30 kunlik seriya"),
    "referral_5": ("👥", "Referral Pro", "5 ta referal"),
    "referral_10": ("💎", "Referral Master", "10 ta referal"),
    "level_3": ("📚", "Bilimdon", "3-darajaga yetish"),
    "level_5": ("🔥", "Ekspert", "5-darajaga yetish"),
}


@router.message(F.text == "👤 Profil")
async def show_profile(message: Message, user: User = None, session=None):
    if user is None:
        return

    status = "💎 Premium" if user.is_premium else "👤 Oddiy"
    if user.is_premium and user.premium_type:
        status = f"💎 {user.premium_type.capitalize()}"

    lang_map = {"uz": "🇺🇿 O'zbek", "ar": "🇸🇦 Arabcha", "en": "🇬🇧 Inglizcha", "ru": "🇷🇺 Ruscha"}
    language = lang_map.get(user.language, user.language)

    join_date = user.created_at.strftime("%d.%m.%Y") if user.created_at else "—"
    level = level_info(user.points)

    _, used, total = await UserService.check_limit(session, user)
    limit_bar = progress_bar(used, total)

    text = (
        f"👤 <b>Profilingiz</b>\n\n"
        f"🆔 ID: <code>{user.telegram_id}</code>\n"
        f"👤 Ism: <b>{user.full_name or '—'}</b>\n"
        f"📱 Username: @{user.username or '—'}\n"
        f"📅 Ro'yxatdan o'tgan: <b>{join_date}</b>\n"
        f"🌐 Til: <b>{language}</b>\n\n"
        f"💎 Holat: <b>{status}</b>\n"
        f"⭐ Ball: <b>{format_number(user.points)}</b>\n"
        f"🏅 Daraja: <b>{level['name']}</b>\n"
        f"<code>{level['progress']}</code>\n\n"
        f"🤖 <b>AI limiti (bugun):</b>\n"
        f"<code>{limit_bar}</code>\n\n"
        f"🔥 Seriya: <b>{user.streak} kun</b>\n"
        f"👥 Referallar: <b>{user.referral_count}</b>\n"
        f"📊 Jami so'rovlar: <b>{format_number(user.total_requests)}</b>"
    )

    await message.answer(
        text,
        reply_markup=profile_keyboard(user.telegram_id),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "profile:achievements")
async def show_achievements(callback: CallbackQuery, user: User = None, session=None):
    if not user or not session:
        return

    result = await session.execute(
        select(Achievement).where(Achievement.telegram_id == user.telegram_id)
    )
    earned = {a.badge for a in result.scalars().all()}

    lines = ["🏅 <b>Yutuqlar (Achievements)</b>\n"]
    for badge, (emoji, name, desc) in ACHIEVEMENT_INFO.items():
        if badge in earned:
            lines.append(f"✅ {emoji} <b>{name}</b> — {desc}")
        else:
            lines.append(f"🔒 ❓ {name} — {desc}")

    await callback.message.edit_text("\n".join(lines), parse_mode="HTML")


@router.callback_query(F.data == "profile:referral")
async def show_referral(callback: CallbackQuery, user: User = None):
    if not user:
        return

    from config.settings import settings
    bot_username = settings.bot_username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user.referral_code}"

    text = (
        f"👥 <b>Referral Tizimi</b>\n\n"
        f"🔗 <b>Sizning havolangiz:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"👥 Taklif qilinganlar: <b>{user.referral_count}</b>\n"
        f"💰 Bonus so'rovlar: <b>{user.bonus_requests}</b>\n\n"
        f"💡 <b>Qanday ishlaydi?</b>\n"
        f"Har taklif qilingan do'stingiz uchun\n"
        f"<b>+10 ta</b> qo'shimcha AI so'rov olasiz! 🎁\n\n"
        f"📣 Do'stlaringizga ulashing va ko'proq AI so'rov ishlating!"
    )
    await callback.message.edit_text(text, parse_mode="HTML")


@router.callback_query(F.data == "profile:daily_bonus")
async def claim_daily(callback: CallbackQuery, user: User = None, session=None):
    if not user or not session:
        return

    claimed, bonus, streak = await UserService.claim_daily_bonus(session, user)

    if not claimed:
        await callback.answer("⏰ Kunlik bonus allaqachon olindi!", show_alert=True)
        return

    await callback.message.edit_text(
        f"🎁 <b>Kunlik bonus!</b>\n\n"
        f"🎉 +{bonus} ball qo'shildi!\n"
        f"🔥 Seriya: <b>{streak} kun</b>\n\n"
        f"{'🌟 Zo\'r! 7 kunlik seriyangiz bor!' if streak >= 7 else ''}"
        f"\n\nErtaga ham keling! 😊",
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("lb:"))
async def show_leaderboard(callback: CallbackQuery, session=None):
    if not session:
        return

    lb_type = callback.data.split(":")[1]

    order_map = {
        "points": (User.points, "⭐ Ball bo'yicha"),
        "requests": (User.total_requests, "🤖 AI So'rovlar bo'yicha"),
        "referrals": (User.referral_count, "👥 Referallar bo'yicha"),
        "streak": (User.streak, "🔥 Seriya bo'yicha"),
    }

    col, title = order_map.get(lb_type, (User.points, "⭐ Ball bo'yicha"))

    result = await session.execute(
        select(User).order_by(col.desc()).limit(10)
    )
    users = result.scalars().all()

    medals = ["🥇", "🥈", "🥉"] + ["4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = [f"🏆 <b>Reyting — {title}</b>\n"]

    for i, u in enumerate(users):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        name = u.username or u.full_name or f"User{u.telegram_id}"
        value = {
            "points": u.points,
            "requests": u.total_requests,
            "referrals": u.referral_count,
            "streak": u.streak,
        }.get(lb_type, 0)
        lines.append(f"{medal} @{name} — <b>{format_number(value)}</b>")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=leaderboard_keyboard(),
        parse_mode="HTML",
    )
