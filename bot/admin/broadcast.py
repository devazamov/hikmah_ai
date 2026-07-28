"""
Hikmah AI — Broadcast Handler
"""
from __future__ import annotations

import asyncio
from typing import Optional

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from bot.filters.admin import IsAdmin
from bot.states import AdminStates
from database.models import User, Broadcast
from utils.helpers import utc_now
from utils.logger import logger

router = Router()
router.message.filter(IsAdmin())


@router.callback_query(F.data == "adm_bc:text")
async def broadcast_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 <b>Broadcast — Matn</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni yozing:\n\n"
        "⚠️ HTML formatlash ishlaydi (bold, italic, code...)\n"
        "Bekor qilish: /cancel",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_broadcast_text)


@router.message(AdminStates.waiting_broadcast_text)
async def send_broadcast_text(message: Message, state: FSMContext, session=None):
    if not session:
        return

    text = message.text or message.caption or ""
    await state.clear()

    # Preview
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    from bot.keyboards.admin_menu import confirm_broadcast_keyboard
    import uuid

    preview_id = str(uuid.uuid4())[:8]

    await message.answer(
        f"👀 <b>Preview:</b>\n\n{text}\n\n"
        f"📊 Barcha faol foydalanuvchilarga yuboriladi.",
        reply_markup=confirm_broadcast_keyboard(preview_id),
        parse_mode="HTML",
    )

    # Store pending broadcast
    bc = Broadcast(
        admin_id=message.from_user.id,
        text=text,
        status="pending",
    )
    session.add(bc)
    await session.commit()

    # Save ID in FSM
    await state.update_data(broadcast_id=bc.id)


@router.callback_query(F.data.startswith("adm_bc:confirm:"))
async def confirm_broadcast(callback: CallbackQuery, session=None, state: FSMContext = None):
    if not session:
        return

    data = await state.get_data() if state else {}
    bc_id = data.get("broadcast_id")

    if not bc_id:
        await callback.answer("❌ Broadcast topilmadi.", show_alert=True)
        return

    result = await session.execute(select(Broadcast).where(Broadcast.id == bc_id))
    bc = result.scalar_one_or_none()
    if not bc:
        await callback.answer("❌ Broadcast topilmadi.", show_alert=True)
        return

    # Get all active users
    users_result = await session.execute(
        select(User.telegram_id).where(User.is_active == True, User.is_banned == False)
    )
    user_ids = [row[0] for row in users_result.all()]

    bc.total_users = len(user_ids)
    bc.status = "running"
    await session.commit()

    await callback.message.edit_text(
        f"📢 <b>Broadcast boshlandi!</b>\n\n"
        f"👥 Foydalanuvchilar: {len(user_ids)}\n"
        f"⏳ Yuborilmoqda...",
        parse_mode="HTML",
    )

    # Send in background
    asyncio.create_task(
        _send_broadcast(callback.bot, user_ids, bc.text, bc, session)
    )


async def _send_broadcast(bot, user_ids, text, bc, session):
    """Send broadcast to all users with rate limiting."""
    sent = 0
    failed = 0

    for uid in user_ids:
        try:
            await bot.send_message(uid, text, parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)  # 20 msg/sec rate limit
        except Exception as e:
            failed += 1
            if "blocked" in str(e).lower() or "deactivated" in str(e).lower():
                # Deactivate user
                result = await session.execute(select(User).where(User.telegram_id == uid))
                user = result.scalar_one_or_none()
                if user:
                    user.is_active = False
                    await session.commit()

    bc.sent_count = sent
    bc.failed_count = failed
    bc.status = "done"
    await session.commit()

    logger.info(f"Broadcast done: {sent} sent, {failed} failed out of {len(user_ids)}")


@router.callback_query(F.data == "adm_bc:cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext = None):
    if state:
        await state.clear()
    await callback.message.edit_text("❌ Broadcast bekor qilindi.")
