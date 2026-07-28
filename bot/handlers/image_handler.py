"""
Hikmah AI — AI Image Generation Handler
Free via Pollinations.ai — no API key needed!
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from ai.features.image_gen import generate_image
from bot.states import AIStates
from database.models import User
from services.user_service import UserService
from utils.helpers import progress_bar
from utils.logger import logger

router = Router()


def image_style_keyboard() -> any:
    builder = InlineKeyboardBuilder()
    styles = [
        ("🎨 Realistik", "realistic"),
        ("🎌 Anime", "anime"),
        ("🎭 Multfilm", "cartoon"),
        ("🖼️ Yog' bo'yoq", "oil_painting"),
        ("💧 Suvrang", "watercolor"),
        ("💻 Raqamli san'at", "digital_art"),
        ("🕌 Islomiy naqsh", "islamic"),
        ("⬜ Minimalist", "minimalist"),
    ]
    for name, key in styles:
        builder.add(InlineKeyboardButton(text=name, callback_data=f"imgstyle:{key}"))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="❌ Bekor", callback_data="img:cancel"))
    return builder.as_markup()


@router.message(F.text.startswith("/imagine") | F.text.startswith("🎨 Rasm"))
async def start_image_gen(message: Message, state: FSMContext, user: User = None, session=None):
    if not user or not session:
        return

    # Check premium for image generation
    if not user.is_premium:
        await message.answer(
            "💎 <b>AI Rasm yaratish — Premium funksiya!</b>\n\n"
            "Premium oling va cheksiz rasm yarating!\n"
            "👉 /premium\n\n"
            "💡 Bepul alternativ: Telegram'da @midjourney_bot dan foydalaning.",
            parse_mode="HTML",
        )
        return

    # Check limits
    can_use, used, total = await UserService.check_limit(session, user)
    if not can_use:
        await message.answer(
            f"❌ <b>Limit tugadi!</b>\n<code>{progress_bar(used, total)}</code>",
            parse_mode="HTML",
        )
        return

    # Check if prompt provided directly
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1 and parts[0] == "/imagine":
        prompt = parts[1].strip()
        await state.update_data(img_prompt=prompt)
        await message.answer(
            f"🎨 <b>Rasm uslubini tanlang:</b>\n\n"
            f"📝 So'rov: <i>{prompt[:100]}</i>",
            reply_markup=image_style_keyboard(),
            parse_mode="HTML",
        )
        return

    await message.answer(
        "🎨 <b>AI Rasm Yaratish</b>\n\n"
        "Rasm uchun tavsif yuboring (inglizcha yaxshiroq):\n\n"
        "💡 Misol:\n"
        "<code>A beautiful mosque at sunset with golden dome</code>\n"
        "<code>Mountain landscape in Uzbekistan, realistic</code>",
        parse_mode="HTML",
    )
    await state.set_state(AIStates.waiting_image)


@router.message(AIStates.waiting_image)
async def get_image_prompt(message: Message, state: FSMContext):
    prompt = message.text.strip()
    await state.update_data(img_prompt=prompt)
    await state.clear()

    await message.answer(
        f"🎨 <b>Rasm uslubini tanlang:</b>\n\n"
        f"📝 So'rov: <i>{prompt[:100]}</i>",
        reply_markup=image_style_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("imgstyle:"))
async def generate_image_handler(callback: CallbackQuery, state: FSMContext, user: User = None, session=None):
    style = callback.data.split(":")[1]
    data = await state.get_data()
    prompt = data.get("img_prompt", "A beautiful landscape")

    await callback.message.edit_text(
        f"🎨 <b>Rasm yaratilmoqda...</b>\n\n"
        f"📝 {prompt[:100]}\n"
        f"🖌️ Uslub: {style}\n\n"
        f"⏳ 10-30 soniya kutib turing...",
        parse_mode="HTML",
    )

    image_bytes, error = await generate_image(prompt=prompt, style=style)

    if error:
        await callback.message.edit_text(error)
        return

    try:
        await callback.message.delete()
        await callback.message.answer_photo(
            BufferedInputFile(image_bytes, filename="hikmah_ai_image.jpg"),
            caption=(
                f"🎨 <b>AI Rasm</b>\n\n"
                f"📝 <i>{prompt[:200]}</i>\n"
                f"🖌️ Uslub: {style}\n\n"
                f"🤖 <b>Hikmah AI</b> tomonidan yaratildi"
            ),
            parse_mode="HTML",
        )
        if user and session:
            await UserService.increment_usage(session, user)
    except Exception as e:
        await callback.message.edit_text(f"❌ Rasm yuborishda xatolik: {e}")


@router.callback_query(F.data == "img:cancel")
async def cancel_image(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Rasm yaratish bekor qilindi.")
