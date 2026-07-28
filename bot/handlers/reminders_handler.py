"""
Hikmah AI — Reminders Handler (with datetime parsing)
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy import select

from bot.states import ToolStates
from database.models import Reminder, User

router = Router()


@router.callback_query(F.data == "tool:reminder")
async def reminder_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⏰ <b>Eslatma Yaratish</b>\n\n"
        "Eslatma matnini yuboring:\n\n"
        "Masalan: <code>Namoz o'qish</code>",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_reminder_text)


@router.message(ToolStates.waiting_reminder_text)
async def get_reminder_text(message: Message, state: FSMContext):
    await state.update_data(reminder_text=message.text.strip())
    await message.answer(
        "✅ Eslatma matni qabul qilindi.\n\n"
        "⏰ Qachon eslatilsin?\n\n"
        "Format:\n"
        "• <code>30m</code> — 30 daqiqadan keyin\n"
        "• <code>2h</code> — 2 soatdan keyin\n"
        "• <code>1d</code> — 1 kundan keyin\n"
        "• <code>20:00</code> — bugun soat 20:00 da",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_reminder_time)


@router.message(ToolStates.waiting_reminder_time)
async def get_reminder_time(message: Message, state: FSMContext, user: User = None, session=None):
    time_str = message.text.strip().lower()
    data = await state.get_data()
    await state.clear()

    now = datetime.now(tz=timezone.utc)
    remind_at = None

    try:
        if re.match(r"^\d+m$", time_str):
            mins = int(time_str[:-1])
            remind_at = now + timedelta(minutes=mins)
        elif re.match(r"^\d+h$", time_str):
            hours = int(time_str[:-1])
            remind_at = now + timedelta(hours=hours)
        elif re.match(r"^\d+d$", time_str):
            days = int(time_str[:-1])
            remind_at = now + timedelta(days=days)
        elif re.match(r"^\d{1,2}:\d{2}$", time_str):
            h, m = map(int, time_str.split(":"))
            remind_at = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if remind_at <= now:
                remind_at += timedelta(days=1)
        else:
            await message.answer("❌ Vaqt formati noto'g'ri. Masalan: <code>30m</code>, <code>2h</code>, <code>20:00</code>", parse_mode="HTML")
            return
    except Exception:
        await message.answer("❌ Vaqt formatida xatolik.")
        return

    if user and session:
        reminder = Reminder(
            telegram_id=user.telegram_id,
            text=data.get("reminder_text", "Eslatma"),
            remind_at=remind_at,
        )
        session.add(reminder)
        await session.commit()

    time_display = remind_at.strftime("%d.%m.%Y %H:%M")
    await message.answer(
        f"✅ <b>Eslatma yaratildi!</b>\n\n"
        f"📝 {data.get('reminder_text', '?')}\n"
        f"⏰ Vaqti: <b>{time_display} UTC</b>",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "tool:my_reminders")
async def my_reminders(callback: CallbackQuery, user: User = None, session=None):
    if not user or not session:
        return

    result = await session.execute(
        select(Reminder)
        .where(Reminder.telegram_id == user.telegram_id, Reminder.is_sent == False)
        .order_by(Reminder.remind_at)
        .limit(5)
    )
    reminders = result.scalars().all()

    if not reminders:
        await callback.message.edit_text("⏰ Hali eslatma yo'q.")
        return

    lines = ["⏰ <b>Mening Eslatmalarim</b>\n"]
    for r in reminders:
        time_str = r.remind_at.strftime("%d.%m %H:%M")
        lines.append(f"• {time_str} — {r.text[:50]}")

    await callback.message.edit_text("\n".join(lines), parse_mode="HTML")
