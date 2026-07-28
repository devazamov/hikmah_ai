"""Hikmah AI — Support Tickets Handler"""
from __future__ import annotations
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.keyboards.main_menu import support_keyboard, cancel_keyboard
from bot.states import SupportStates
from database.models import User, SupportTicket
from utils.helpers import utc_now
from utils.logger import logger

router = Router()


@router.message(F.text == "🎫 Support")
async def support_menu(message: Message):
    await message.answer(
        "🎫 <b>Qo'llab-quvvatlash</b>\n\n"
        "Savol, taklif yoki muammoingizni bildiring:",
        reply_markup=support_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("support:"))
async def handle_support(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(":")[1]
    topics = {
        "question": "❓ Savol",
        "bug": "🐛 Xato",
        "suggestion": "💡 Taklif",
    }
    if action in topics:
        await callback.message.edit_text(
            f"{topics[action]}\n\nMurojaat mavzusini yozing:",
            parse_mode="HTML",
        )
        await state.set_state(SupportStates.waiting_subject)
        await state.update_data(ticket_type=action)
    elif action == "my_tickets":
        await callback.message.edit_text("🎫 Tiketlar bo'limi ishlab chiqilmoqda...")


@router.message(SupportStates.waiting_subject)
async def ticket_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text.strip())
    await message.answer("✅ Mavzu qabul qilindi.\n\nBatafsil matnni yozing:")
    await state.set_state(SupportStates.waiting_message)


@router.message(SupportStates.waiting_message)
async def ticket_message(message: Message, state: FSMContext, user: User = None, session=None):
    data = await state.get_data()
    await state.clear()

    if user and session:
        ticket = SupportTicket(
            telegram_id=user.telegram_id,
            subject=data.get("subject", "Mavzusiz"),
            message=message.text or "",
        )
        session.add(ticket)
        await session.commit()

        # Notify admins
        from config.settings import settings
        for admin_id in settings.admin_ids_list:
            try:
                await message.bot.send_message(
                    admin_id,
                    f"🎫 <b>Yangi Tiket #{ticket.id}</b>\n\n"
                    f"👤 Foydalanuvchi: {user.full_name} ({user.telegram_id})\n"
                    f"📌 Mavzu: {ticket.subject}\n\n"
                    f"💬 Xabar:\n{ticket.message[:500]}",
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.warning(f"Cannot notify admin {admin_id}: {e}")

    await message.answer(
        "✅ <b>Murojaat qabul qilindi!</b>\n\n"
        "Tez orada javob beramiz. Rahmat! 🙏",
        parse_mode="HTML",
    )
