"""
Hikmah AI — Quran Audio Handler (Qori Bot)
"""
from __future__ import annotations

import random

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from ai.features.tts import quran_audio_url

router = Router()

RECITERS = [
    ("🎵 Mishary Rashid", "ar.alafasy"),
    ("🎵 Abdul Basit", "ar.abdulbasitmurattal"),
    ("🎵 Husary", "ar.husary"),
    ("🎵 Sa'ud Shuraym", "ar.shaatree"),
    ("🎵 Minshawi", "ar.minshawi"),
]

FAMOUS_SURAHS = [
    (1, "Al-Fotiha — Ochilish surasi"),
    (36, "Yasin — Qur'on yuragi"),
    (55, "Ar-Rahman — Rahmon"),
    (56, "Al-Voqia — Voqia"),
    (67, "Al-Mulk — Mulk"),
    (78, "An-Naba — Xabar"),
    (112, "Al-Ikhlos — Ikhlos"),
    (113, "Al-Falaq — Tong"),
    (114, "An-Nas — Odamlar"),
]


def reciter_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for name, code in RECITERS:
        builder.row(InlineKeyboardButton(text=name, callback_data=f"qori:{code}"))
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="islamic:back"))
    return builder.as_markup()


def surah_keyboard(reciter: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for num, name in FAMOUS_SURAHS:
        builder.add(InlineKeyboardButton(
            text=f"📖 {num}. {name.split('—')[0].strip()}",
            callback_data=f"qori_play:{reciter}:{num}"
        ))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="◀️ Qori tanlash", callback_data="islamic:quran_audio"))
    return builder.as_markup()


@router.callback_query(F.data == "islamic:quran_audio")
async def qori_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎵 <b>Qori Bot — Qur'on Audio</b>\n\n"
        "Qori (Reciter) tanlang:",
        reply_markup=reciter_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("qori:"))
async def select_surah(callback: CallbackQuery):
    reciter = callback.data.split(":", 1)[1]
    reciter_name = next((n for n, c in RECITERS if c == reciter), reciter)

    await callback.message.edit_text(
        f"🎵 <b>{reciter_name}</b>\n\nSurani tanlang:",
        reply_markup=surah_keyboard(reciter),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("qori_play:"))
async def play_surah(callback: CallbackQuery):
    parts = callback.data.split(":", 2)
    reciter = parts[1]
    surah_num = int(parts[2])

    surah_name = next((n for num, n in FAMOUS_SURAHS if num == surah_num), f"Sura {surah_num}")
    audio_url = await quran_audio_url(surah_num, reciter)
    reciter_name = next((n for n, c in RECITERS if c == reciter), reciter)

    await callback.message.edit_text(
        f"🎵 <b>{surah_name}</b>\n"
        f"👤 Qori: {reciter_name}\n\n"
        f"🔗 Tinglash uchun:\n{audio_url}\n\n"
        f"📌 Yuklab olish uchun havolani bosing.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Tinglash", url=audio_url)],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"qori:{reciter}")],
        ]),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
