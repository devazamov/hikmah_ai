"""
Hikmah AI — Games & Challenges Handler
Daily Islamic quiz, word games, brain teasers
"""
from __future__ import annotations

import random

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database.models import User
from services.user_service import UserService

router = Router()

ISLAMIC_QUIZ = [
    {
        "q": "Qur'on nechta suradan iborat?",
        "options": ["114", "112", "120", "110"],
        "correct": 0,
        "points": 10,
    },
    {
        "q": "Islomning besh rukni qaysi to'g'ri tartibda?",
        "options": [
            "Shahodat, Namoz, Ro'za, Zakot, Haj",
            "Namoz, Shahodat, Zakot, Haj, Ro'za",
            "Haj, Namoz, Ro'za, Zakot, Shahodat",
            "Zakot, Namoz, Shahodat, Haj, Ro'za",
        ],
        "correct": 0,
        "points": 15,
    },
    {
        "q": "Qur'onning eng uzun surasi qaysi?",
        "options": ["Al-Baqara", "Al-Imron", "An-Niso", "Al-Maidah"],
        "correct": 0,
        "points": 10,
    },
    {
        "q": "Ramadonda necha kun ro'za tutiladi?",
        "options": ["29 yoki 30", "28", "31", "27"],
        "correct": 0,
        "points": 5,
    },
    {
        "q": "Qaysi shaharda Ka'ba joylashgan?",
        "options": ["Makka", "Madina", "Quddus", "Bag'dod"],
        "correct": 0,
        "points": 5,
    },
    {
        "q": "Payg'ambarimiz Muhammad (s.a.v.) necha yoshida vafot etgan?",
        "options": ["63", "60", "70", "55"],
        "correct": 0,
        "points": 10,
    },
    {
        "q": "Qur'onning eng qisqa surasi qaysi?",
        "options": ["Al-Kawthar", "Al-Ikhlos", "Al-Asr", "Al-Falaq"],
        "correct": 0,
        "points": 10,
    },
]

WORD_GAME_WORDS = [
    ("HIKMAT", "Bilim va donolik"),
    ("BARAKAH", "Ko'payish, farovonlik"),
    ("SABR", "Chidamlilik, toqat"),
    ("SHUKR", "Minnatdorlik"),
    ("TAQVO", "Allohdan qo'rqish va yaxshi amal"),
    ("IMON", "Ishonch, e'tiqod"),
    ("EHSON", "Yaxshilik qilish"),
    ("SIDQ", "Rostgo'ylik"),
]


def quiz_keyboard(quiz_id: int, options: list) -> any:
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(options):
        builder.row(InlineKeyboardButton(
            text=opt,
            callback_data=f"quiz:{quiz_id}:{i}"
        ))
    return builder.as_markup()


@router.message(F.text == "🎮 O'yinlar")
async def games_menu(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🕌 Islomiy Quiz", callback_data="game:quiz"),
        InlineKeyboardButton(text="🔤 So'z O'yini", callback_data="game:word"),
    )
    builder.row(
        InlineKeyboardButton(text="🧩 Topishmoq", callback_data="game:riddle"),
        InlineKeyboardButton(text="🎯 Viktorina", callback_data="game:trivia"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Mening natijam", callback_data="game:my_score"),
    )

    await message.answer(
        "🎮 <b>O'yinlar va Musobaqalar</b>\n\n"
        "O'ynang va ball toping! ⭐\n\n"
        "Har to'g'ri javob = ball!",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "game:quiz")
async def start_quiz(callback: CallbackQuery):
    quiz = random.choice(ISLAMIC_QUIZ)
    idx = ISLAMIC_QUIZ.index(quiz)

    # Shuffle options but track correct
    options = quiz["options"].copy()
    correct_answer = options[quiz["correct"]]
    random.shuffle(options)
    new_correct = options.index(correct_answer)

    await callback.message.edit_text(
        f"🕌 <b>Islomiy Quiz</b>\n\n"
        f"❓ {quiz['q']}\n\n"
        f"⭐ To'g'ri javob uchun: <b>+{quiz['points']} ball</b>",
        reply_markup=quiz_keyboard(idx, options),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("quiz:"))
async def answer_quiz(callback: CallbackQuery, user: User = None, session=None):
    parts = callback.data.split(":")
    quiz_id = int(parts[1])
    answer_idx = int(parts[2])

    quiz = ISLAMIC_QUIZ[quiz_id]
    options = quiz["options"].copy()
    correct_answer = options[quiz["correct"]]

    # Find what was clicked
    clicked_option = callback.message.reply_markup.inline_keyboard[answer_idx][0].text
    is_correct = clicked_option == correct_answer

    if is_correct:
        if user and session:
            user.points += quiz["points"]
            await session.commit()

        await callback.message.edit_text(
            f"✅ <b>To'g'ri!</b>\n\n"
            f"🎉 +{quiz['points']} ball qo'shildi!\n"
            f"📌 Javob: <b>{correct_answer}</b>\n\n"
            f"⭐ Jami ballingiz: <b>{user.points if user else '?'}</b>",
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            f"❌ <b>Noto'g'ri!</b>\n\n"
            f"📌 To'g'ri javob: <b>{correct_answer}</b>\n\n"
            f"Qaytadan: /start → 🎮 O'yinlar",
            parse_mode="HTML",
        )

    await callback.answer("✅" if is_correct else "❌")


@router.callback_query(F.data == "game:word")
async def word_game(callback: CallbackQuery):
    word, hint = random.choice(WORD_GAME_WORDS)
    hidden = " ".join("_" * len(word))

    await callback.message.edit_text(
        f"🔤 <b>So'z O'yini</b>\n\n"
        f"Bu so'zni toping!\n\n"
        f"<code>{hidden}</code>\n\n"
        f"💡 Maslahat: {hint}\n"
        f"📊 Harflar soni: {len(word)}\n\n"
        f"Javobni yozing:",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "game:riddle")
async def show_riddle(callback: CallbackQuery):
    riddles = [
        ("Men qanchalik ko'p ishlatsangiz, shunchalik ozaman. Men kimman?", "Karandash"),
        ("Doim yuguramanu, hech qachon charchamayman. Men kimman?", "Soat"),
        ("Ko'zlari bor, ammo ko'rmayman. Tishim bor, ammo chaynamayman. Men kimman?", "Taroq"),
        ("Kechasi uchaman, kunduz dam olaman. Men kimman?", "Boyqush"),
        ("Qancha ko'p olsangiz, shunchalik ko'p qoladi. Bu nima?", "Bilim"),
    ]
    riddle, answer = random.choice(riddles)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💡 Javobni ko'r", callback_data=f"riddle:ans:{answer}"))
    builder.row(InlineKeyboardButton(text="🔄 Boshqasi", callback_data="game:riddle"))

    await callback.message.edit_text(
        f"🧩 <b>Topishmoq</b>\n\n{riddle}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("riddle:ans:"))
async def riddle_answer(callback: CallbackQuery):
    answer = callback.data.split(":", 2)[2]
    await callback.answer(f"💡 Javob: {answer}", show_alert=True)
