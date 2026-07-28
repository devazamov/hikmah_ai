"""
Hikmah AI — Premium Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from bot.keyboards.main_menu import premium_keyboard, cancel_keyboard
from bot.states import AdminStates
from database.models import User, PromoCode
from services.user_service import UserService
from utils.helpers import utc_now, progress_bar
from utils.logger import logger

router = Router()

PREMIUM_PLANS = {
    "basic": {"name": "🥉 Basic", "days": 30, "limit": 150, "description": "150 so'rov/kun"},
    "pro": {"name": "🥈 Pro", "days": 30, "limit": 300, "description": "300 so'rov/kun"},
    "ultra": {"name": "🥇 Ultra", "days": 30, "limit": 999999, "description": "Cheksiz so'rovlar"},
}


@router.message(F.text.in_({"💎 Premium Olish", "💎 Premium Panel"}))
async def show_premium(message: Message, user: User = None):
    if not user:
        return

    if user.is_premium:
        expires = user.premium_expires.strftime("%d.%m.%Y") if user.premium_expires else "?"
        text = (
            f"💎 <b>Premium Hisobingiz</b>\n\n"
            f"✅ Holat: <b>{user.premium_type or 'Premium'}</b>\n"
            f"📅 Muddati: <b>{expires}</b>\n\n"
            f"🤖 Kunlik limit: <b>{PREMIUM_PLANS.get(user.premium_type or '', {}).get('limit', 300)}</b>\n\n"
            f"💡 Premium imkoniyatlaridan to'liq foydalaning!"
        )
    else:
        text = (
            f"💎 <b>Hikmah AI Premium</b>\n\n"
            f"✅ Barcha AI modellar\n"
            f"✅ Yuqori daily limit\n"
            f"✅ AI rasm yaratish\n"
            f"✅ PDF bilan suhbat\n"
            f"✅ Ovoz → Matn\n"
            f"✅ Video yuklab olish\n"
            f"✅ Ustuvor javob tezligi\n\n"
            f"📦 <b>Rejalar:</b>\n"
            f"🥉 Basic — 150 so'rov/kun\n"
            f"🥈 Pro — 300 so'rov/kun\n"
            f"🥇 Ultra — Cheksiz so'rovlar\n\n"
            f"🎟️ Promo kod: /promo\n"
            f"📞 To'lov: Admin bilan bog'laning @HikmahSupport"
        )

    await message.answer(text, reply_markup=premium_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("premium:"))
async def premium_action(callback: CallbackQuery, user: User = None, state: FSMContext = None):
    action = callback.data.split(":")[1]

    if action == "promo":
        await callback.message.edit_text(
            "🎟️ <b>Promo Kod</b>\n\nPromo kodingizni yuboring:",
            parse_mode="HTML",
        )
        if state:
            await state.set_state(AdminStates.waiting_promo_code)
        return

    plan = PREMIUM_PLANS.get(action)
    if not plan:
        await callback.answer("❌ Noto'g'ri reja.", show_alert=True)
        return

    await callback.message.edit_text(
        f"💎 <b>{plan['name']} Reja</b>\n\n"
        f"✅ {plan['description']}\n"
        f"📅 Muddat: {plan['days']} kun\n\n"
        f"💳 To'lov uchun admin bilan bog'laning:\n"
        f"👤 @HikmahSupport\n\n"
        f"📌 Xabar yuborganda '<b>{plan['name']}</b> sotib olmoqchiman' deying.",
        parse_mode="HTML",
    )


@router.message(AdminStates.waiting_promo_code)
async def use_promo_code(message: Message, state: FSMContext, user: User = None, session=None):
    await state.clear()
    code = message.text.strip().upper()

    if not session or not user:
        return

    result = await session.execute(
        select(PromoCode).where(PromoCode.code == code)
    )
    promo = result.scalar_one_or_none()

    if not promo:
        await message.answer("❌ <b>Promo kod topilmadi!</b>", parse_mode="HTML")
        return

    if promo.used_count >= promo.max_uses:
        await message.answer("❌ <b>Bu promo kod limitiga yetdi!</b>", parse_mode="HTML")
        return

    if promo.expires_at and promo.expires_at < utc_now():
        await message.answer("❌ <b>Bu promo kod muddati tugagan!</b>", parse_mode="HTML")
        return

    # Apply promo
    promo.used_count += 1
    benefits = []

    if promo.premium_type:
        await UserService.set_premium(session, user, promo.premium_type, 30)
        benefits.append(f"💎 {promo.premium_type.capitalize()} Premium (30 kun)")

    if promo.bonus_requests:
        user.bonus_requests += promo.bonus_requests
        benefits.append(f"🤖 +{promo.bonus_requests} ta bonus so'rov")

    if promo.bonus_points:
        user.points += promo.bonus_points
        benefits.append(f"⭐ +{promo.bonus_points} ball")

    await session.commit()

    await message.answer(
        f"🎉 <b>Promo kod ishlatildi!</b>\n\n"
        f"✅ Olgan sovg'alaringiz:\n"
        + "\n".join(f"• {b}" for b in benefits),
        parse_mode="HTML",
    )
