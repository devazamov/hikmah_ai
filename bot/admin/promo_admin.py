"""
Hikmah AI — Admin Promo Code Management
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from bot.filters.admin import IsAdmin
from bot.states import AdminStates
from database.models import PromoCode
from utils.helpers import generate_promo_code, utc_now
from utils.logger import logger

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "adm_promo:create")
async def create_promo_start(callback: CallbackQuery, state: FSMContext):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🥉 Basic (30 kun)", callback_data="adm_promo:type:basic"),
        InlineKeyboardButton(text="🥈 Pro (30 kun)", callback_data="adm_promo:type:pro"),
    )
    builder.row(
        InlineKeyboardButton(text="🥇 Ultra (30 kun)", callback_data="adm_promo:type:ultra"),
        InlineKeyboardButton(text="⭐ Faqat Ball", callback_data="adm_promo:type:points"),
    )
    builder.row(
        InlineKeyboardButton(text="🤖 Faqat So'rovlar", callback_data="adm_promo:type:requests"),
    )

    await callback.message.edit_text(
        "🎟️ <b>Promo Kod Yaratish</b>\n\nPromo kod turi:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_promo:type:"))
async def promo_set_type(callback: CallbackQuery, state: FSMContext):
    ptype = callback.data.split(":")[-1]
    await state.update_data(promo_type=ptype)

    await callback.message.edit_text(
        f"✅ Tur: {ptype}\n\n"
        "Necha marta ishlatilsin? (raqam yuboring):\n"
        "Masalan: <code>1</code> yoki <code>100</code>",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_promo_type)


@router.message(AdminStates.waiting_promo_type)
async def promo_set_uses(message: Message, state: FSMContext, session=None):
    try:
        max_uses = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Raqam kiriting.")
        return

    data = await state.get_data()
    ptype = data.get("promo_type", "basic")
    await state.clear()

    # Generate code
    code = generate_promo_code(10)

    # Defaults by type
    premium_type = None
    bonus_requests = 0
    bonus_points = 0

    if ptype == "basic":
        premium_type = "basic"
        bonus_requests = 50
    elif ptype == "pro":
        premium_type = "pro"
        bonus_requests = 100
    elif ptype == "ultra":
        premium_type = "ultra"
        bonus_requests = 200
    elif ptype == "points":
        bonus_points = 500
    elif ptype == "requests":
        bonus_requests = 100

    if session:
        promo = PromoCode(
            code=code,
            premium_type=premium_type,
            bonus_requests=bonus_requests,
            bonus_points=bonus_points,
            max_uses=max_uses,
            created_by=message.from_user.id,
        )
        session.add(promo)
        await session.commit()

    await message.answer(
        f"✅ <b>Promo Kod Yaratildi!</b>\n\n"
        f"🎟️ Kod: <code>{code}</code>\n"
        f"📦 Tur: {ptype}\n"
        f"🔄 Ishlatish: {max_uses} marta\n"
        f"💎 Premium: {premium_type or '—'}\n"
        f"🤖 Bonus so'rovlar: {bonus_requests}\n"
        f"⭐ Bonus ball: {bonus_points}\n\n"
        f"📲 Foydalanuvchilarga kodni ulashing!",
        parse_mode="HTML",
    )
    logger.info(f"Promo code created: {code} by admin {message.from_user.id}")


@router.callback_query(F.data == "adm_promo:list")
async def list_promos(callback: CallbackQuery, session=None):
    if not session:
        return
    result = await session.execute(
        select(PromoCode).order_by(PromoCode.created_at.desc()).limit(15)
    )
    promos = result.scalars().all()

    if not promos:
        await callback.answer("Hali promo kod yo'q.", show_alert=True)
        return

    lines = ["🎟️ <b>Promo Kodlar</b>\n"]
    for p in promos:
        status = "✅" if p.used_count < p.max_uses else "❌"
        lines.append(
            f"{status} <code>{p.code}</code> | {p.used_count}/{p.max_uses} | {p.premium_type or 'bonus'}"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
    )
