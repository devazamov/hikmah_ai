"""
Hikmah AI — /start Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from bot.keyboards.main_menu import main_reply_keyboard, subscription_keyboard
from database.models import User
from services.channel_service import ChannelService
from services.user_service import UserService
from utils.helpers import get_greeting
from utils.logger import logger

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user: User = None, session=None, is_new_user: bool = False):
    # Check subscription
    subscribed, unsubscribed = await ChannelService.check_subscription(
        bot=message.bot, user_id=message.from_user.id
    )

    if not subscribed:
        channels = await ChannelService.get_channel_invite_links(message.bot, unsubscribed)
        ch_text = "\n".join(
            f"• <a href='{ch.get('invite_link') or ''}'>{ch['title']}</a>"
            if ch.get("invite_link") or ch.get("username")
            else f"• {ch['title']}"
            for ch in channels
        )
        await message.answer(
            f"❌ <b>Majburiy obuna!</b>\n\n"
            f"Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n\n"
            f"{ch_text}\n\n"
            f"✅ Obuna bo'lgandan so'ng <b>Tekshirish</b> tugmasini bosing.",
            reply_markup=subscription_keyboard(channels),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        return

    if user is None:
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
        return

    # Handle referral from deep link
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_") and is_new_user:
        ref_code = args[1][4:]
        if session:
            from sqlalchemy import select
            from database.models import User as UserModel
            res = await session.execute(
                select(UserModel).where(UserModel.referral_code == ref_code)
            )
            referrer = res.scalar_one_or_none()
            if referrer and referrer.telegram_id != user.telegram_id:
                await UserService.add_referral_bonus(session, referrer.telegram_id, 10)
                logger.info(f"Referral: {user.telegram_id} referred by {referrer.telegram_id}")

    name = user.first_name or user.full_name or "Do'stim"
    greeting = get_greeting(name)

    # Daily bonus for returning user
    bonus_text = ""
    if user and session and not is_new_user:
        claimed, bonus, streak = await UserService.claim_daily_bonus(session, user)
        if claimed:
            bonus_text = f"\n\n🎁 <b>Kunlik bonus:</b> +{bonus} ball! 🔥 Seriya: {streak} kun"

    welcome_text = (
        f"{greeting}\n\n"
        f"🤖 <b>Hikmah AI</b> — O'zbekiston uchun professional AI platformasi\n\n"
        f"✨ <b>Imkoniyatlar:</b>\n"
        f"• 🧠 AI Chat (Gemini, Groq, OpenRouter)\n"
        f"• 🕌 Islomiy AI (Qur'on, Hadis, Namoz vaqtlari)\n"
        f"• 🎬 Kino Bot (kodli tizim)\n"
        f"• 📥 Video yuklab olish (YouTube, Instagram...)\n"
        f"• 🎨 AI Rasm, 🌤️ Ob-havo, 💱 Valyuta va ko'p narsalar!\n"
        f"{bonus_text}\n\n"
        f"📌 Boshlash uchun pastdagi menyudan foydalaning 👇"
    )

    await message.answer(
        welcome_text,
        reply_markup=main_reply_keyboard(user.is_premium),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "check:subscription")
async def check_subscription(callback: CallbackQuery, user: User = None):
    subscribed, unsubscribed = await ChannelService.check_subscription(
        bot=callback.bot, user_id=callback.from_user.id
    )

    if subscribed:
        await callback.message.edit_text(
            "✅ <b>Obuna tasdiqlandi!</b>\n\n"
            "Hikmah AI ga xush kelibsiz! /start bosing.",
            parse_mode="HTML",
        )
    else:
        channels = await ChannelService.get_channel_invite_links(callback.bot, unsubscribed)
        await callback.answer("❌ Hali obuna bo'lmagansiz!", show_alert=True)


@router.callback_query(F.data == "main:back")
async def back_to_main(callback: CallbackQuery, user: User = None):
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Asosiy menyu",
        reply_markup=main_reply_keyboard(user.is_premium if user else False),
    )
