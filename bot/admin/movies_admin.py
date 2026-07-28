"""
Hikmah AI — Admin Movie Management
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Video, Document
from sqlalchemy import select, delete

from bot.filters.admin import IsAdmin
from bot.states import AdminStates
from database.models import Movie
from utils.helpers import generate_promo_code
from utils.logger import logger

router = Router()
router.message.filter(IsAdmin())

_pending_movie: dict = {}


@router.callback_query(F.data == "adm_mv:add")
async def add_movie_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎬 <b>Yangi Kino Qo'shish</b>\n\n"
        "1️⃣ Kino nomini yuboring (inglizcha):",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_movie_data)
    await state.update_data(step="title")


@router.message(AdminStates.waiting_movie_data)
async def add_movie_steps(message: Message, state: FSMContext, session=None):
    data = await state.get_data()
    step = data.get("step", "title")

    if step == "title":
        await state.update_data(title=message.text.strip(), step="code")
        code = generate_promo_code(6).upper()
        await message.answer(
            f"✅ Nomi: {message.text.strip()}\n\n"
            f"2️⃣ Kino kodini kiriting yoki bu avtomatik kod foydalaning:\n"
            f"<code>MV{code}</code>\n\n"
            f"Yoki o'z kodingizni yozing:",
            parse_mode="HTML",
        )
        await state.update_data(auto_code=f"MV{code}")

    elif step == "code":
        code = message.text.strip().upper()
        await state.update_data(code=code, step="description")
        await message.answer(
            f"✅ Kod: {code}\n\n"
            f"3️⃣ Kino tavsifini yuboring (yoki /skip bosing):"
        )

    elif step == "description":
        desc = None if message.text == "/skip" else message.text.strip()
        await state.update_data(description=desc, step="file")
        await message.answer(
            "4️⃣ Video faylni yuboring (yoki /skip — keyinroq qo'shishingiz mumkin):"
        )

    elif step == "file":
        await state.update_data(step="confirm")
        if message.video or message.document:
            file_id = message.video.file_id if message.video else message.document.file_id
            await state.update_data(file_id=file_id)
            await message.answer("✅ Fayl qabul qilindi.")
        else:
            await message.answer("⚠️ Fayl yo'q — keyinroq qo'shiladi.")

        # Save movie
        movie_data = await state.get_data()
        await state.clear()

        if not session:
            return

        movie = Movie(
            code=movie_data.get("code", "MV000"),
            title=movie_data.get("title", "Nomsiz"),
            description=movie_data.get("description"),
            file_id=movie_data.get("file_id"),
            channel_id=message.chat.id,
            message_id=message.message_id,
        )
        session.add(movie)
        await session.commit()

        await message.answer(
            f"✅ <b>Kino qo'shildi!</b>\n\n"
            f"🎬 {movie.title}\n"
            f"📌 Kod: <code>{movie.code}</code>",
            parse_mode="HTML",
        )


@router.callback_query(F.data == "adm_mv:list")
async def list_all_movies(callback: CallbackQuery, session=None):
    if not session:
        return

    result = await session.execute(
        select(Movie).order_by(Movie.created_at.desc()).limit(20)
    )
    movies = result.scalars().all()

    if not movies:
        await callback.message.edit_text("❌ Hali kino yo'q.")
        return

    text = "🎬 <b>Kinolar Ro'yxati</b>\n\n"
    for m in movies:
        status = "✅" if m.is_active else "❌"
        text += f"{status} <code>{m.code}</code> — {m.title[:30]} ({m.views} 👁️)\n"

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm:movies"))

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
