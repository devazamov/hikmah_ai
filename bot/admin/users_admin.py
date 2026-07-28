"""
Hikmah AI — Admin User Management Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, desc

from bot.filters.admin import IsAdmin
from bot.keyboards.admin_menu import admin_user_actions_keyboard
from bot.states import AdminStates
from database.models import User
from services.user_service import UserService
from utils.helpers import format_number, utc_now, progress_bar
from utils.logger import logger

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "adm_usr:search_id")
async def search_by_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 <b>Foydalanuvchi ID bilan qidirish</b>\n\n"
        "Telegram ID yuboring:",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_user_id)
    await state.update_data(search_type="id")


@router.callback_query(F.data == "adm_usr:search_un")
async def search_by_username(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 <b>Username bilan qidirish</b>\n\n"
        "@username yuboring:",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_user_id)
    await state.update_data(search_type="username")


@router.message(AdminStates.waiting_user_id)
async def find_user(message: Message, state: FSMContext, session=None):
    data = await state.get_data()
    search_type = data.get("search_type", "id")
    query_val = message.text.strip().lstrip("@")

    if not session:
        return

    if search_type == "id":
        try:
            tid = int(query_val)
            result = await session.execute(select(User).where(User.telegram_id == tid))
        except ValueError:
            await message.answer("❌ Noto'g'ri ID. Faqat raqam kiriting.")
            return
    else:
        result = await session.execute(select(User).where(User.username == query_val))

    user = result.scalar_one_or_none()
    await state.clear()

    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi.")
        return

    await show_user_info(message, user)


async def show_user_info(message: Message, user: User):
    """Show detailed user info with action buttons."""
    status = "💎 Premium" if user.is_premium else "👤 Oddiy"
    ban_status = "🚫 Bloklangan" if user.is_banned else "✅ Faol"
    premium_exp = user.premium_expires.strftime("%d.%m.%Y") if user.premium_expires else "—"

    text = (
        f"👤 <b>Foydalanuvchi Ma'lumoti</b>\n\n"
        f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
        f"👤 Ism: <b>{user.full_name}</b>\n"
        f"📱 Username: @{user.username or '—'}\n"
        f"🌐 Til: <b>{user.language}</b>\n\n"
        f"💎 Holat: <b>{status}</b>\n"
        f"📅 Premium tugashi: <b>{premium_exp}</b>\n"
        f"🔒 Ban: <b>{ban_status}</b>\n\n"
        f"⭐ Ball: <b>{format_number(user.points)}</b>\n"
        f"📊 Jami so'rovlar: <b>{format_number(user.total_requests)}</b>\n"
        f"👥 Referallar: <b>{user.referral_count}</b>\n"
        f"🔥 Seriya: <b>{user.streak}</b>\n\n"
        f"📅 Ro'yxatdan: <b>{user.created_at.strftime('%d.%m.%Y %H:%M') if user.created_at else '?'}</b>\n"
        f"🕐 So'nggi faollik: <b>{user.last_active.strftime('%d.%m.%Y %H:%M') if user.last_active else '?'}</b>"
    )
    await message.answer(
        text,
        reply_markup=admin_user_actions_keyboard(user.telegram_id, user.is_banned, user.is_premium),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_usr:ban:"))
async def admin_ban_user(callback: CallbackQuery, session=None):
    tid = int(callback.data.split(":")[-1])
    if not session:
        return
    result = await session.execute(select(User).where(User.telegram_id == tid))
    user = result.scalar_one_or_none()
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)
        return
    await UserService.ban(session, user)
    await callback.answer(f"🚫 {user.full_name} bloklandi!", show_alert=True)
    logger.info(f"Admin {callback.from_user.id} banned user {tid}")

    try:
        await callback.bot.send_message(
            tid,
            "🚫 <b>Siz botdan bloklangansiz.</b>\n\nMurojaat: @HikmahSupport",
            parse_mode="HTML",
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("adm_usr:unban:"))
async def admin_unban_user(callback: CallbackQuery, session=None):
    tid = int(callback.data.split(":")[-1])
    if not session:
        return
    result = await session.execute(select(User).where(User.telegram_id == tid))
    user = result.scalar_one_or_none()
    if not user:
        await callback.answer("❌ Topilmadi.", show_alert=True)
        return
    await UserService.unban(session, user)
    await callback.answer(f"✅ {user.full_name} unban qilindi!", show_alert=True)
    try:
        await callback.bot.send_message(
            tid,
            "✅ <b>Bloklash olib tashlandi.</b> Botdan foydalanishingiz mumkin!",
            parse_mode="HTML",
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("adm_usr:add_prem:"))
async def admin_give_prem(callback: CallbackQuery, state: FSMContext):
    tid = int(callback.data.split(":")[-1])
    await state.update_data(target_user_id=tid)
    from bot.keyboards.admin_menu import admin_premium_keyboard
    await callback.message.edit_text(
        f"💎 <b>Premium berish</b>\n\nFoydalanuvchi: <code>{tid}</code>\n\nReja tanlang:",
        reply_markup=admin_premium_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_usr:rem_prem:"))
async def admin_remove_prem(callback: CallbackQuery, session=None):
    tid = int(callback.data.split(":")[-1])
    if not session:
        return
    result = await session.execute(select(User).where(User.telegram_id == tid))
    user = result.scalar_one_or_none()
    if not user:
        await callback.answer("❌ Topilmadi.", show_alert=True)
        return
    await UserService.remove_premium(session, user)
    await callback.answer("✅ Premium olib tashlandi!", show_alert=True)
    try:
        await callback.bot.send_message(tid, "ℹ️ Premium obunangiz tugatildi.")
    except Exception:
        pass


@router.callback_query(F.data.startswith("adm_usr:msg:"))
async def admin_msg_user(callback: CallbackQuery, state: FSMContext):
    tid = int(callback.data.split(":")[-1])
    await state.update_data(msg_target=tid)
    await callback.message.edit_text(
        f"✉️ <b>Xabar yuborish</b>\n\nFoydalanuvchi: <code>{tid}</code>\n\nXabarni yozing:",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_msg_to_user)


@router.message(AdminStates.waiting_msg_to_user)
async def send_msg_to_user(message: Message, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("msg_target")
    await state.clear()

    if not target_id:
        await message.answer("❌ Xato.")
        return

    try:
        await message.bot.send_message(
            target_id,
            f"📩 <b>Admin xabari:</b>\n\n{message.text}",
            parse_mode="HTML",
        )
        await message.answer(f"✅ Xabar {target_id} ga yuborildi!")
    except Exception as e:
        await message.answer(f"❌ Xabar yuborishda xatolik: {e}")


@router.callback_query(F.data == "adm_usr:list_prem")
async def list_premium_users(callback: CallbackQuery, session=None):
    if not session:
        return
    result = await session.execute(
        select(User).where(User.is_premium == True).order_by(desc(User.premium_expires)).limit(15)
    )
    users = result.scalars().all()
    if not users:
        await callback.answer("Premium foydalanuvchilar yo'q.", show_alert=True)
        return

    lines = ["💎 <b>Premium Foydalanuvchilar</b>\n"]
    for u in users:
        exp = u.premium_expires.strftime("%d.%m") if u.premium_expires else "?"
        lines.append(f"• {u.full_name or u.username or u.telegram_id} [{u.premium_type}] → {exp}")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=None,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_usr:top_points")
async def top_users_by_points(callback: CallbackQuery, session=None):
    if not session:
        return
    result = await session.execute(
        select(User).order_by(desc(User.points)).limit(10)
    )
    users = result.scalars().all()
    medals = ["🥇", "🥈", "🥉"] + ["4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = ["⭐ <b>Top 10 — Ball bo'yicha</b>\n"]
    for i, u in enumerate(users):
        name = u.username or u.full_name or str(u.telegram_id)
        lines.append(f"{medals[i]} {name} — {format_number(u.points)} ball")
    await callback.message.edit_text("\n".join(lines), parse_mode="HTML")
