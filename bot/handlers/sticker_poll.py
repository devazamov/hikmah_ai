"""
Hikmah AI — Sticker Maker & Poll Creator Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from services.sticker_service import create_text_sticker, image_to_sticker
from services.poll_service import create_ai_poll, create_quiz
from services.ai_service import AIService
from bot.states import ToolStates
from database.models import User

router = Router()


# ── Sticker Maker ────────────────────────────────

@router.callback_query(F.data == "tool:sticker")
async def sticker_start(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Matndan sticker", callback_data="sticker:text"),
        InlineKeyboardButton(text="🖼️ Rasmdan sticker", callback_data="sticker:image"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="main:back"))

    await callback.message.edit_text(
        "🖼️ <b>Sticker Maker</b>\n\nSticker turini tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "sticker:text")
async def sticker_from_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 <b>Matndan Sticker</b>\n\n"
        "Sticker matni va emoji yuboring.\n"
        "Format: <code>Matn | 😊</code>\n\n"
        "Masalan: <code>Hikmah AI | 🤖</code>",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_qr_text)  # Reuse state


@router.callback_query(F.data == "sticker:image")
async def sticker_from_image(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🖼️ <b>Rasmdan Sticker</b>\n\n"
        "Rasm yuboring — men uni sticker formatiga o'tkazaman!",
        parse_mode="HTML",
    )


@router.message(F.photo)
async def photo_to_sticker(message: Message, state: FSMContext):
    """Convert photo to sticker."""
    current_state = await state.get_state()

    file = await message.bot.get_file(message.photo[-1].file_id)
    photo_bytes = await message.bot.download_file(file.file_path)

    processing = await message.answer("⏳ Sticker yaratilmoqda...")
    webp_bytes, error = await image_to_sticker(photo_bytes.read())
    await processing.delete()

    if error:
        await message.answer(error)
        return

    await message.answer_sticker(
        BufferedInputFile(webp_bytes, filename="sticker.webp"),
    )
    await message.answer(
        "✅ <b>Sticker tayyor!</b>\n\n"
        "📌 Stickerni saqlash uchun:\n"
        "• Uzoq bosing → 'Sticker saqlash'\n"
        "• Yoki @Stickers botiga yuboring",
        parse_mode="HTML",
    )


# ── Poll Creator ─────────────────────────────────

@router.callback_query(F.data == "tool:poll")
async def poll_start(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Oddiy So'rovnoma", callback_data="poll:normal"),
        InlineKeyboardButton(text="❓ Viktorina (Quiz)", callback_data="poll:quiz"),
    )
    builder.row(
        InlineKeyboardButton(text="🤖 AI So'rovnoma", callback_data="poll:ai"),
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="main:back"))

    await callback.message.edit_text(
        "📊 <b>So'rovnoma Yaratish</b>\n\nTurni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "poll:normal")
async def create_normal_poll(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📊 <b>So'rovnoma</b>\n\n"
        "Format (har qatorda bittadan):\n\n"
        "<code>Savol matni?\n"
        "Javob 1\n"
        "Javob 2\n"
        "Javob 3</code>",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_note_content)  # Reuse state
    await state.update_data(poll_type="normal")


@router.callback_query(F.data == "poll:ai")
async def create_ai_poll_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🤖 <b>AI So'rovnoma</b>\n\n"
        "Mavzu yuboring — AI so'rovnoma yaratadi:\n\n"
        "Masalan: <code>Uyda qanday hayvon boqasiz?</code>",
        parse_mode="HTML",
    )
    await state.update_data(poll_type="ai")
    await state.set_state(ToolStates.waiting_note_title)


@router.message(ToolStates.waiting_note_title)
async def handle_ai_poll_topic(message: Message, state: FSMContext, user: User = None, session=None):
    data = await state.get_data()
    if data.get("poll_type") != "ai":
        return

    topic = message.text.strip()
    await state.clear()

    processing = await message.answer("🤖 So'rovnoma tayyorlanmoqda...")

    prompt = (
        f"'{topic}' mavzusida Telegram uchun qiziqarli so'rovnoma yarat.\n"
        "Format:\n"
        "SAVOL: [savol matni]\n"
        "JAVOB1: [javob]\n"
        "JAVOB2: [javob]\n"
        "JAVOB3: [javob]\n"
        "JAVOB4: [javob]"
    )

    from ai import ai_manager, Message as AIMsg
    response = await ai_manager.chat(messages=[AIMsg(role="user", content=prompt)])
    await processing.delete()

    if not response.success:
        await message.answer("❌ So'rovnoma yaratishda xatolik.")
        return

    # Parse response
    lines = response.text.strip().split("\n")
    question = ""
    options = []
    for line in lines:
        if line.startswith("SAVOL:"):
            question = line.replace("SAVOL:", "").strip()
        elif any(line.startswith(f"JAVOB{i}:") for i in range(1, 11)):
            opt = line.split(":", 1)[-1].strip()
            if opt:
                options.append(opt)

    if not question or len(options) < 2:
        await message.answer("❌ AI to'g'ri format yaratmadi. Qaytadan urinib ko'ring.")
        return

    success = await create_ai_poll(message.bot, message.chat.id, question, options)
    if not success:
        await message.answer("❌ So'rovnoma yaratishda Telegram xatosi.")
