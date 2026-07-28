"""
Hikmah AI — Feedback & Review Handler
"""
from __future__ import annotations
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from database.models import User
from utils.logger import logger

router = Router()

def rating_keyboard() -> any:
    builder = InlineKeyboardBuilder()
    stars = [("⭐", 1), ("⭐⭐", 2), ("⭐⭐⭐", 3), ("⭐⭐⭐⭐", 4), ("⭐⭐⭐⭐⭐", 5)]
    for label, val in stars:
        builder.add(InlineKeyboardButton(text=label, callback_data=f"fb:rate:{val}"))
    builder.adjust(5)
    builder.row(InlineKeyboardButton(text="❌ Bekor", callback_data="fb:cancel"))
    return builder.as_markup()


@router.message(F.text == "⭐ Fikr bildirish")
async def feedback_start(message: Message):
    await message.answer(
        "⭐ <b>Fikr-mulohaza</b>\n\nHikmah AI'ni baholang:",
        reply_markup=rating_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("fb:rate:"))
async def feedback_rate(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split(":")[-1])
    await state.update_data(rating=rating)

    star_text = "⭐" * rating
    await callback.message.edit_text(
        f"Rahmat! {star_text}\n\nQo'shimcha fikringiz (ixtiyoriy):",
        parse_mode="HTML",
    )
    from bot.states import SupportStates
    await state.set_state(SupportStates.waiting_message)
    await state.update_data(feedback_mode=True)


@router.callback_query(F.data == "fb:cancel")
async def feedback_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.")


@router.message(F.text == "/feedback")
async def feedback_cmd(message: Message):
    await feedback_start(message)
