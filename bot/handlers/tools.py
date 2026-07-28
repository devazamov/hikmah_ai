"""
Hikmah AI — Tools Handler (Weather, Currency, QR, URL, Calculator, Notes, Reminders)
"""
from __future__ import annotations

import io
import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message, CallbackQuery

from bot.keyboards.main_menu import tools_keyboard, cancel_keyboard, video_quality_keyboard
from bot.states import ToolStates
from database.models import User
from services.weather_service import get_weather
from services.currency_service import convert_currency, popular_rates
from services.video_service import download_video, get_video_info
from utils.logger import logger

router = Router()


@router.message(F.text == "🛠️ Vositalar")
async def show_tools(message: Message):
    await message.answer(
        "🛠️ <b>Vositalar</b>\n\nQuyidagilardan birini tanlang:",
        reply_markup=tools_keyboard(),
        parse_mode="HTML",
    )


# ── Weather ──────────────────────────────────────────────

@router.callback_query(F.data == "tool:weather")
async def ask_weather_city(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🌤️ <b>Ob-havo</b>\n\nShahar nomini yuboring:\n\n"
        "Masalan: <code>Toshkent</code>, <code>Samarkand</code>",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_city_weather)


@router.message(ToolStates.waiting_city_weather)
async def get_weather_result(message: Message, state: FSMContext):
    await state.clear()
    result = await get_weather(message.text.strip())
    await message.answer(result or "❌ Ob-havo ma'lumoti topilmadi.", parse_mode="HTML")


# ── Currency ─────────────────────────────────────────────

@router.callback_query(F.data == "tool:currency")
async def show_currency(callback: CallbackQuery, state: FSMContext):
    rates_text = await popular_rates()
    await callback.message.edit_text(
        f"{rates_text}\n\n"
        f"💱 <b>Konvertatsiya:</b>\n"
        f"Format: <code>100 USD UZS</code>\n"
        f"Yoki: <code>50000 UZS EUR</code>",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_currency_input)


@router.message(ToolStates.waiting_currency_input)
async def convert_currency_handler(message: Message, state: FSMContext):
    parts = message.text.strip().upper().split()
    if len(parts) != 3:
        await message.answer("❌ Format: <code>100 USD UZS</code>", parse_mode="HTML")
        return
    try:
        amount = float(parts[0])
        from_cur, to_cur = parts[1], parts[2]
        await state.clear()
        _, text = await convert_currency(amount, from_cur, to_cur)
        await message.answer(text, parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Noto'g'ri format. Masalan: <code>100 USD UZS</code>", parse_mode="HTML")


# ── Calculator ───────────────────────────────────────────

@router.callback_query(F.data == "tool:calc")
async def ask_calc(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔢 <b>Kalkulyator</b>\n\n"
        "Hisoblash ifodani yuboring:\n\n"
        "Masalan:\n"
        "<code>2 + 2</code>\n"
        "<code>15 * 8 / 2</code>\n"
        "<code>sqrt(144)</code>\n"
        "<code>sin(30)</code>",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_calc_input)


@router.message(ToolStates.waiting_calc_input)
async def calculate(message: Message, state: FSMContext):
    await state.clear()
    expr = message.text.strip()
    try:
        import math
        # Safe evaluation
        allowed = set("0123456789+-*/()., eiπ")
        safe_expr = (
            expr.replace("^", "**")
            .replace("sqrt", "math.sqrt")
            .replace("sin", "math.sin")
            .replace("cos", "math.cos")
            .replace("tan", "math.tan")
            .replace("log", "math.log10")
            .replace("ln", "math.log")
            .replace("pi", "math.pi")
            .replace("π", "math.pi")
        )
        result = eval(safe_expr, {"__builtins__": {}, "math": math})
        await message.answer(
            f"🔢 <b>Hisob natijasi:</b>\n\n"
            f"<code>{expr}</code> = <b>{result}</b>",
            parse_mode="HTML",
        )
    except Exception:
        await message.answer("❌ Noto'g'ri ifoda. Qaytadan urinib ko'ring.")


# ── QR Code ──────────────────────────────────────────────

@router.callback_query(F.data == "tool:qr")
async def ask_qr(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📱 <b>QR Kod Generatori</b>\n\n"
        "QR kod yaratish uchun matn yoki URL yuboring:",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_qr_text)


@router.message(ToolStates.waiting_qr_text)
async def generate_qr(message: Message, state: FSMContext):
    await state.clear()
    try:
        import qrcode
        text = message.text.strip()
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        await message.answer_photo(
            BufferedInputFile(buf.read(), filename="qrcode.png"),
            caption=f"📱 <b>QR Kod</b>\n<code>{text[:100]}</code>",
            parse_mode="HTML",
        )
    except ImportError:
        await message.answer("❌ qrcode kutubxonasi o'rnatilmagan.")
    except Exception as e:
        await message.answer(f"❌ QR kod yaratishda xatolik: {e}")


# ── URL Shortener ────────────────────────────────────────

@router.callback_query(F.data == "tool:url")
async def ask_url(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔗 <b>URL Qisqartirish</b>\n\n"
        "Qisqartirmoqchi bo'lgan URL ni yuboring:",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_url_to_shorten)


@router.message(ToolStates.waiting_url_to_shorten)
async def shorten_url(message: Message, state: FSMContext):
    await state.clear()
    url = message.text.strip()
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://tinyurl.com/api-create.php?url={url}",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    short = await resp.text()
                    await message.answer(
                        f"🔗 <b>Qisqartirilgan URL:</b>\n\n"
                        f"📌 Asl: <code>{url[:60]}...</code>\n"
                        f"✅ Qisqa: <code>{short}</code>",
                        parse_mode="HTML",
                    )
                else:
                    await message.answer("❌ URL qisqartirishda xatolik.")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")


# ── Video Download ───────────────────────────────────────

@router.callback_query(F.data == "tool:video")
async def ask_video(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📥 <b>Video Yuklab Olish</b>\n\n"
        "Video havolasini yuboring:\n\n"
        "✅ Qo'llab-quvvatlanadi:\n"
        "• YouTube\n"
        "• Instagram\n"
        "• TikTok\n"
        "• Facebook\n"
        "• Twitter/X\n"
        "• VK va ko'p boshqalar\n\n"
        "⚠️ Maksimal hajm: 50 MB",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_video_url)


@router.message(ToolStates.waiting_video_url)
async def download_video_handler(message: Message, state: FSMContext):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        await message.answer("❌ URL noto'g'ri. https:// bilan boshlang.")
        return

    await state.clear()

    # Get video info first
    processing = await message.answer("⏳ Video ma'lumotlari olinmoqda...")
    info = await get_video_info(url)

    if info:
        text = (
            f"🎬 <b>{info['title'][:60]}</b>\n"
            f"👤 Yuklagan: {info.get('uploader', '?')}\n"
            f"⏱️ Davomiyligi: {info.get('duration', 0) // 60} daq\n\n"
            f"📥 Yuklash boshlandi..."
        )
        await processing.edit_text(text, parse_mode="HTML")
    else:
        await processing.edit_text("⏳ Video yuklanmoqda...")

    file_path, error = await download_video(url)

    if error:
        await message.answer(f"❌ {error}")
        return

    try:
        with open(file_path, "rb") as f:
            await message.answer_video(
                BufferedInputFile(f.read(), filename="video.mp4"),
                caption=f"✅ <b>Yuklab olindi!</b>\n🤖 Hikmah AI",
                parse_mode="HTML",
            )
        # Cleanup
        import os
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"❌ Yuborishda xatolik: {e}")


# ── Notes ────────────────────────────────────────────────

@router.callback_query(F.data == "tool:notes")
async def notes_menu(callback: CallbackQuery, session=None, user: User = None):
    if not session or not user:
        return

    from sqlalchemy import select
    from database.models import Note
    result = await session.execute(
        select(Note).where(Note.telegram_id == user.telegram_id).order_by(Note.created_at.desc()).limit(5)
    )
    notes = result.scalars().all()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Yangi Eslatma", callback_data="note:new"))
    for note in notes:
        builder.row(InlineKeyboardButton(
            text=f"📓 {note.title[:30]}",
            callback_data=f"note:view:{note.id}"
        ))
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="main:back"))

    text = f"📓 <b>Eslatmalar</b>\n\nJami: {len(notes)} ta\n\n" + (
        "\n".join(f"• {n.title}" for n in notes) if notes else "Hali eslatma yo'q."
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "note:new")
async def new_note(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📓 <b>Yangi Eslatma</b>\n\nEslatma sarlavhasini yuboring:",
        parse_mode="HTML",
    )
    await state.set_state(ToolStates.waiting_note_title)


@router.message(ToolStates.waiting_note_title)
async def note_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("✅ Sarlavha saqlandi.\n\nEndi eslatma matnini yuboring:")
    await state.set_state(ToolStates.waiting_note_content)


@router.message(ToolStates.waiting_note_content)
async def note_content(message: Message, state: FSMContext, user: User = None, session=None):
    data = await state.get_data()
    await state.clear()

    if user and session:
        from database.models import Note
        note = Note(
            telegram_id=user.telegram_id,
            title=data.get("title", "Sarlavhasiz"),
            content=message.text.strip(),
        )
        session.add(note)
        await session.commit()

    await message.answer(
        "✅ <b>Eslatma saqlandi!</b>\n\n"
        f"📌 <b>{data.get('title', '?')}</b>",
        parse_mode="HTML",
    )
