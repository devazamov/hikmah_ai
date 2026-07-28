"""
Hikmah AI — Movie Bot Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.main_menu import movie_keyboard, cancel_keyboard
from bot.states import MovieStates
from database.models import User, Movie
from sqlalchemy import select, or_
from utils.logger import logger

router = Router()


@router.message(F.text == "🎬 Kino Bot")
async def movie_menu(message: Message):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔍 Qidiruv", callback_data="movie:search"),
        InlineKeyboardButton(text="📋 Yangi Kinolar", callback_data="movie:list"),
    )
    builder.row(
        InlineKeyboardButton(text="🕌 Islomiy Kinolar", callback_data="movie:islamic"),
        InlineKeyboardButton(text="❓ Kod bilan Olish", callback_data="movie:by_code"),
    )

    await message.answer(
        "🎬 <b>Kino Bot</b>\n\n"
        "Kinolarni kod orqali yoki qidiruv orqali toping!\n\n"
        "📌 <b>Foydalanish:</b>\n"
        "• Kod yuboring (masalan: <code>MV001</code>)\n"
        "• Yoki qidiruv tugmasini bosing\n"
        "• Islomiy kinolar alohida bo'limda",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "movie:by_code")
async def ask_movie_code(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎬 <b>Kod bilan Kino</b>\n\n"
        "Kino kodini yuboring:\n"
        "Masalan: <code>MV001</code>",
        parse_mode="HTML",
    )
    await state.set_state(MovieStates.waiting_code)


@router.message(MovieStates.waiting_code)
async def get_movie_by_code(message: Message, state: FSMContext, session=None):
    code = message.text.strip().upper()
    await state.clear()

    if not session:
        return

    result = await session.execute(
        select(Movie).where(Movie.code == code, Movie.is_active == True)
    )
    movie = result.scalar_one_or_none()

    if not movie:
        await message.answer(
            f"❌ <b>{code}</b> kodli kino topilmadi.\n\n"
            "Boshqa kod kiriting yoki qidiruvdan foydalaning.",
            parse_mode="HTML",
        )
        return

    await send_movie(message, movie, session)


async def send_movie(message: Message, movie: Movie, session):
    """Send movie info and file."""
    from sqlalchemy import select, update
    # Increment views
    movie.views += 1
    await session.commit()

    info_text = (
        f"🎬 <b>{movie.title}</b>\n"
        f"{f'🇺🇿 {movie.title_uz}' if movie.title_uz else ''}\n\n"
        f"{'📅 Yil: ' + str(movie.year) if movie.year else ''}\n"
        f"{'🎭 Janr: ' + movie.genre if movie.genre else ''}\n"
        f"{'🌐 Til: ' + movie.language if movie.language else ''}\n\n"
        f"{movie.description[:200] if movie.description else ''}\n\n"
        f"📌 Kod: <code>{movie.code}</code>\n"
        f"👁️ Ko'rishlar: {movie.views}"
    )

    if movie.file_id:
        try:
            await message.answer_video(
                video=movie.file_id,
                caption=info_text,
                parse_mode="HTML",
            )
            return
        except Exception:
            pass

    # If no file, try forwarding from channel
    if movie.channel_id and movie.message_id:
        try:
            await message.bot.forward_message(
                chat_id=message.chat.id,
                from_chat_id=movie.channel_id,
                message_id=movie.message_id,
            )
            await message.answer(info_text, parse_mode="HTML")
            return
        except Exception as e:
            logger.error(f"Forward movie error: {e}")

    await message.answer(
        info_text + "\n\n⚠️ Fayl vaqtincha mavjud emas.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "movie:search")
async def ask_movie_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 <b>Kino Qidiruv</b>\n\nKino nomini yuboring:",
        parse_mode="HTML",
    )
    await state.set_state(MovieStates.waiting_search_query)


@router.message(MovieStates.waiting_search_query)
async def search_movies(message: Message, state: FSMContext, session=None):
    query = message.text.strip()
    await state.clear()

    if not session:
        return

    result = await session.execute(
        select(Movie).where(
            or_(
                Movie.title.ilike(f"%{query}%"),
                Movie.title_uz.ilike(f"%{query}%"),
                Movie.description.ilike(f"%{query}%"),
                Movie.genre.ilike(f"%{query}%"),
            ),
            Movie.is_active == True,
        ).limit(10)
    )
    movies = result.scalars().all()

    if not movies:
        await message.answer(f"❌ <b>'{query}'</b> bo'yicha kino topilmadi.", parse_mode="HTML")
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    for m in movies:
        builder.row(InlineKeyboardButton(
            text=f"🎬 {m.title[:35]} ({m.year or '?'})",
            callback_data=f"movie:get:{m.code}"
        ))

    await message.answer(
        f"🔍 <b>'{query}' bo'yicha natijalar:</b> {len(movies)} ta",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("movie:get:"))
async def get_movie_callback(callback: CallbackQuery, session=None):
    code = callback.data.split(":", 2)[2]

    if not session:
        return

    result = await session.execute(
        select(Movie).where(Movie.code == code, Movie.is_active == True)
    )
    movie = result.scalar_one_or_none()

    if not movie:
        await callback.answer("❌ Kino topilmadi!", show_alert=True)
        return

    await callback.message.delete()
    await send_movie(callback.message, movie, session)


@router.callback_query(F.data == "movie:list")
async def list_movies(callback: CallbackQuery, session=None):
    if not session:
        return

    result = await session.execute(
        select(Movie).where(Movie.is_active == True)
        .order_by(Movie.created_at.desc()).limit(10)
    )
    movies = result.scalars().all()

    if not movies:
        await callback.message.edit_text("❌ Hali kino yo'q.")
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    for m in movies:
        builder.row(InlineKeyboardButton(
            text=f"🎬 {m.title[:35]}",
            callback_data=f"movie:get:{m.code}"
        ))

    await callback.message.edit_text(
        f"🎬 <b>Yangi kinolar:</b> {len(movies)} ta",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "movie:islamic")
async def islamic_movies(callback: CallbackQuery, session=None):
    if not session:
        return

    result = await session.execute(
        select(Movie).where(Movie.is_active == True, Movie.is_islamic == True)
        .order_by(Movie.created_at.desc()).limit(10)
    )
    movies = result.scalars().all()

    if not movies:
        await callback.message.edit_text(
            "🕌 <b>Islomiy Kinolar</b>\n\nHali islomiy kino qo'shilmagan.",
            parse_mode="HTML",
        )
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    for m in movies:
        builder.row(InlineKeyboardButton(
            text=f"🕌 {m.title[:35]}",
            callback_data=f"movie:get:{m.code}"
        ))

    await callback.message.edit_text(
        f"🕌 <b>Islomiy Kinolar:</b> {len(movies)} ta",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
