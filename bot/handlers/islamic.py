"""
Hikmah AI — Islamic Features Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.main_menu import islamic_keyboard, cancel_keyboard
from bot.states import IslamicStates
from database.models import User
from services.islamic_service import (
    get_quran_ayah, get_prayer_times,
    get_random_dua, get_random_hadith,
)
from services.ai_service import AIService
from utils.logger import logger

router = Router()


@router.message(F.text == "🕌 Islomiy")
async def islamic_menu(message: Message, user: User = None):
    await message.answer(
        "🕌 <b>Islomiy Bo'lim</b>\n\n"
        "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ\n\n"
        "Islomiy bilimlar, Qur'on, Hadis va namoz vaqtlari:",
        reply_markup=islamic_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "islamic:quran")
async def ask_quran(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📖 <b>Qur'on Oyati</b>\n\n"
        "Sura raqamini yuboring (1-114):\n\n"
        "Masalan: <code>2</code> (Al-Baqara)",
        parse_mode="HTML",
    )
    await state.set_state(IslamicStates.waiting_surah)


@router.message(IslamicStates.waiting_surah)
async def get_surah(message: Message, state: FSMContext):
    try:
        surah = int(message.text.strip())
        if not 1 <= surah <= 114:
            await message.answer("❌ Sura raqami 1-114 orasida bo'lishi kerak.")
            return
        await state.update_data(surah=surah)
        await message.answer(
            f"✅ Sura: {surah}\n\nEndi oyat raqamini yuboring:",
        )
        await state.set_state(IslamicStates.waiting_ayah)
    except ValueError:
        await message.answer("❌ Raqam kiriting. Masalan: <code>2</code>", parse_mode="HTML")


@router.message(IslamicStates.waiting_ayah)
async def get_ayah(message: Message, state: FSMContext):
    try:
        ayah = int(message.text.strip())
        data = await state.get_data()
        surah = data.get("surah", 1)

        await state.clear()
        processing = await message.answer("📖 Qur'on ma'lumotlari yuklanmoqda...")

        result = await get_quran_ayah(surah, ayah)
        await processing.delete()
        await message.answer(result or "❌ Oyat topilmadi.", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Raqam kiriting. Masalan: <code>5</code>", parse_mode="HTML")


@router.callback_query(F.data == "islamic:prayer")
async def ask_prayer_city(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🕌 <b>Namoz Vaqtlari</b>\n\n"
        "Shahar nomini yuboring (inglizcha):\n\n"
        "Masalan: <code>Tashkent</code>, <code>Samarkand</code>, <code>Mecca</code>",
        parse_mode="HTML",
    )
    await state.set_state(IslamicStates.waiting_city_prayer)


@router.message(IslamicStates.waiting_city_prayer)
async def get_prayer(message: Message, state: FSMContext):
    city = message.text.strip()
    await state.clear()

    processing = await message.answer("🕌 Namoz vaqtlari yuklanmoqda...")
    result = await get_prayer_times(city)
    await processing.delete()

    if result:
        await message.answer(result, parse_mode="HTML")
    else:
        await message.answer(f"❌ '{city}' uchun namoz vaqtlari topilmadi.")


@router.callback_query(F.data == "islamic:dua")
async def show_dua(callback: CallbackQuery):
    dua = get_random_dua()
    await callback.message.edit_text(dua, parse_mode="HTML")


@router.callback_query(F.data == "islamic:hadith")
async def show_hadith(callback: CallbackQuery):
    hadith = get_random_hadith()
    await callback.message.edit_text(hadith, parse_mode="HTML")


@router.callback_query(F.data == "islamic:question")
async def islamic_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "❓ <b>Islomiy Savol</b>\n\n"
        "Islomiy savol yoki muammoingizni yozing.\n"
        "AI Qur'on va hadislar asosida javob beradi:",
        parse_mode="HTML",
    )
    await state.set_state(IslamicStates.waiting_question)


@router.message(IslamicStates.waiting_question)
async def answer_islamic_question(message: Message, state: FSMContext, user: User = None, session=None):
    await state.clear()
    processing = await message.answer("🕌 Islomiy javob tayyorlanmoqda...")

    response = await AIService.islamic_answer(message.text)
    await processing.delete()

    if response.success:
        await message.answer(
            f"🕌 <b>Islomiy Javob:</b>\n\n{response.text}",
            parse_mode="HTML",
        )
    else:
        await message.answer("❌ Javob berishda xatolik. Keyinroq urinib ko'ring.")


@router.callback_query(F.data == "islamic:qibla")
async def show_qibla(callback: CallbackQuery):
    await callback.message.edit_text(
        "🕋 <b>Qibla Yo'nalishi</b>\n\n"
        "📍 Makkatul Mukarrama koordinatalar:\n"
        "<code>21.3891° N, 39.8579° E</code>\n\n"
        "🧭 Qibla topish uchun:\n"
        "• Telefon kompasidan foydalaning\n"
        "• qibla.com saytiga kiring\n"
        "• Masjidda so'rang\n\n"
        "🌐 Online Qibla: <a href='https://www.qibla.com'>qibla.com</a>",
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "islamic:calendar")
async def show_islamic_calendar(callback: CallbackQuery):
    from datetime import datetime
    now = datetime.now()
    text = (
        f"📅 <b>Islomiy Takvim</b>\n\n"
        f"🗓️ Milodiy: <b>{now.strftime('%d %B %Y')}</b>\n\n"
        f"📌 <b>Islomiy oylar:</b>\n"
        f"1. Muharram (Muqaddas oy)\n"
        f"2. Safar\n"
        f"3. Rabi ul-Avval (Mavlud oyi)\n"
        f"4. Rabi ul-Oxir\n"
        f"5. Jumad ul-Avval\n"
        f"6. Jumad ul-Oxir\n"
        f"7. Rajab (Muqaddas oy)\n"
        f"8. Sha'bon\n"
        f"9. Ramazon (Ro'za oyi) 🌙\n"
        f"10. Shavvol\n"
        f"11. Zul-Qa'da\n"
        f"12. Zul-Hijja (Haj oyi)\n\n"
        f"🌐 Aniq hisob uchun: <a href='https://www.islamicfinder.org/islamic-calendar'>IslamicFinder</a>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", disable_web_page_preview=True)
