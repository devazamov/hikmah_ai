"""Hikmah AI — /help Handler"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.models import User

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message, user: User = None):
    text = (
        "📚 <b>Hikmah AI — Yordam</b>\n\n"
        "🤖 <b>Asosiy buyruqlar:</b>\n"
        "/start — Boshlanish\n"
        "/help — Ushbu yordam\n"
        "/profile — Profilingiz\n"
        "/premium — Premium ma'lumot\n"
        "/promo — Promo kod ishlatish\n\n"
        "🕌 <b>Islomiy:</b>\n"
        "• <b>🕌 Islomiy</b> tugmasini bosing\n\n"
        "🎬 <b>Kino:</b>\n"
        "• <b>🎬 Kino Bot</b> → Kod yuboring\n\n"
        "🛠️ <b>Vositalar:</b>\n"
        "• <b>🛠️ Vositalar</b> tugmasini bosing\n\n"
        "🤖 <b>AI Chat:</b>\n"
        "• Istalgan matn → AI javob beradi\n\n"
        "📞 <b>Yordam:</b> @HikmahSupport"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("profile"))
async def cmd_profile(message: Message, user: User = None, session=None):
    from bot.handlers.profile import show_profile
    await show_profile(message, user=user, session=session)


@router.message(Command("premium"))
async def cmd_premium(message: Message, user: User = None):
    from bot.handlers.premium import show_premium
    await show_premium(message, user=user)


@router.message(Command("promo"))
async def cmd_promo(message: Message, state=None):
    await message.answer(
        "🎟️ <b>Promo Kod</b>\n\nPromo kodingizni yuboring:",
        parse_mode="HTML",
    )
    if state:
        from bot.states import AdminStates
        await state.set_state(AdminStates.waiting_promo_code)
