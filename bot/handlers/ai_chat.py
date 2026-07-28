"""
Hikmah AI — AI Chat Handler (Main Feature)
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from database.models import User
from services.user_service import UserService
from services.ai_service import AIService
from utils.helpers import get_limit_text, progress_bar
from utils.logger import logger

router = Router()


async def _check_and_reply(message: Message, user: User, session) -> bool:
    """Check AI limit. Return True if user can proceed."""
    can_use, used, total = await UserService.check_limit(session, user)
    if not can_use:
        bar = progress_bar(used, total)
        await message.answer(
            f"❌ <b>Bugungi AI limiti tugadi!</b>\n\n"
            f"<code>{bar}</code>\n\n"
            f"⏰ Limit ertaga <b>00:00 UTC</b> da yangilanadi.\n"
            f"💎 /premium — limitni oshirish",
            parse_mode="HTML",
        )
        return False
    return True


@router.message(F.text == "🤖 AI Chat")
async def ai_chat_menu(message: Message, user: User = None):
    await message.answer(
        "🤖 <b>AI Chat</b>\n\n"
        "Istalgan savolingizni yozing — men javob beraman!\n\n"
        "💡 <b>Maslahat:</b> Qanchalik aniq savol — shunchalik yaxshi javob.\n\n"
        "📌 Istalgan vaqt /start orqali menyuga qaytishingiz mumkin.",
        parse_mode="HTML",
    )


@router.message(F.text & ~F.text.startswith("/"))
async def handle_ai_message(message: Message, user: User = None, session=None):
    """Main AI chat handler — processes all text messages."""
    if user is None or session is None:
        return

    # Skip menu buttons
    menu_texts = {
        "🤖 AI Chat", "🕌 Islomiy", "🎬 Kino Bot", "🛠️ Vositalar",
        "👤 Profil", "⚙️ Sozlamalar", "💎 Premium Olish", "💎 Premium Panel",
        "❌ Bekor qilish",
    }
    if message.text in menu_texts:
        return

    # Check limit
    if not await _check_and_reply(message, user, session):
        return

    # Show typing
    thinking = await message.answer("🤔 O'ylayapman...", parse_mode="HTML")

    try:
        response = await AIService.chat(
            session=session,
            user=user,
            user_message=message.text,
        )

        # Update usage stats
        await UserService.increment_usage(session, user)

        # Check for new achievements
        new_badges = await UserService.check_achievements(session, user)

        await thinking.delete()

        if not response.success:
            await message.answer(
                f"❌ <b>AI xatosi:</b>\n{response.error or 'Nomaʼlum xatolik'}",
                parse_mode="HTML",
            )
            return

        # Format response
        text = response.text
        if len(text) > 4000:
            # Split into chunks
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                await message.answer(chunk, parse_mode="HTML")
        else:
            await message.answer(text, parse_mode="HTML")

        # Show current limit
        _, used, total = await UserService.check_limit(session, user)
        bar = progress_bar(used, total)
        await message.answer(
            f"<code>{bar}</code>",
            parse_mode="HTML",
        )

        # Achievement notifications
        badge_names = {
            "first_message": "🎉 Birinchi xabar!",
            "power_user": "🌟 Kuchli foydalanuvchi (100 so'rov)!",
            "ai_master": "🏆 AI Master (1000 so'rov)!",
            "level_3": "⬆️ Darajangiz 3 ga ko'tarildi!",
            "level_5": "⬆️ Darajangiz 5 ga ko'tarildi!",
            "streak_7": "🔥 7 kunlik seriya! Ajoyib!",
        }
        for badge in new_badges:
            if badge in badge_names:
                await message.answer(f"🏅 <b>Yutuq:</b> {badge_names[badge]}", parse_mode="HTML")

    except Exception as e:
        logger.error(f"AI chat error for {user.telegram_id}: {e}")
        await thinking.delete()
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.",
            parse_mode="HTML",
        )


@router.callback_query(F.data == "settings:clear_history")
async def clear_chat_history(callback: CallbackQuery, user: User = None):
    if user:
        AIService.clear_history(user.telegram_id)
    await callback.answer("✅ Suhbat tarixi tozalandi!", show_alert=True)
