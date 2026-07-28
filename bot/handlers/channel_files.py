"""
Hikmah AI — Channel Files Search & Download Handler
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy import select, or_

from database.models import ChannelFile
from bot.states import ToolStates

router = Router()

FILE_TYPE_ICONS = {
    "pdf": "📄",
    "video": "🎬",
    "audio": "🎵",
    "zip": "🗜️",
    "apk": "📱",
    "doc": "📝",
    "image": "🖼️",
    "other": "📎",
}


def file_categories_keyboard() -> any:
    builder = InlineKeyboardBuilder()
    categories = [
        ("📄 PDF", "pdf"),
        ("🎬 Video", "video"),
        ("🎵 Audio", "audio"),
        ("🗜️ ZIP/RAR", "zip"),
        ("📱 APK", "apk"),
        ("📝 Hujjat", "doc"),
        ("🖼️ Rasm", "image"),
    ]
    for name, ftype in categories:
        builder.add(InlineKeyboardButton(text=name, callback_data=f"cfiles:{ftype}"))
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text="🔍 Qidiruv", callback_data="cfiles:search"),
    )
    return builder.as_markup()


@router.message(F.text == "📁 Kanal Fayllari")
async def channel_files_menu(message: Message):
    await message.answer(
        "📁 <b>Kanal Fayllari</b>\n\n"
        "Kanallarimizda joylashgan fayllarni qidiring va yuklab oling!\n\n"
        "Kategoriya tanlang:",
        reply_markup=file_categories_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("cfiles:") & ~F.data.startswith("cfiles:get:"))
async def show_files_by_type(callback: CallbackQuery, session=None, state: FSMContext = None):
    action = callback.data.split(":")[1]

    if action == "search":
        await callback.message.edit_text(
            "🔍 <b>Fayl Qidiruv</b>\n\nQidirish uchun fayl nomini yuboring:",
            parse_mode="HTML",
        )
        if state:
            await state.set_state(ToolStates.waiting_youtube_url)  # Reuse
            await state.update_data(search_type="file")
        return

    if not session:
        return

    result = await session.execute(
        select(ChannelFile)
        .where(ChannelFile.file_type == action)
        .order_by(ChannelFile.downloads.desc())
        .limit(10)
    )
    files = result.scalars().all()

    if not files:
        await callback.message.edit_text(
            f"{FILE_TYPE_ICONS.get(action, '📎')} <b>Bu turda fayl topilmadi.</b>",
            parse_mode="HTML",
        )
        return

    builder = InlineKeyboardBuilder()
    for f in files:
        name = f.file_name or f"Fayl #{f.id}"
        icon = FILE_TYPE_ICONS.get(f.file_type, "📎")
        size_mb = f"{f.file_size / 1024 / 1024:.1f} MB" if f.file_size else "?"
        builder.row(InlineKeyboardButton(
            text=f"{icon} {name[:35]} ({size_mb})",
            callback_data=f"cfiles:get:{f.id}"
        ))

    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="cfiles:back"))

    await callback.message.edit_text(
        f"{FILE_TYPE_ICONS.get(action, '📎')} <b>{action.upper()} Fayllar</b>:\n\n"
        f"Jami: {len(files)} ta topildi",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("cfiles:get:"))
async def send_channel_file(callback: CallbackQuery, session=None):
    file_id_db = int(callback.data.split(":")[-1])

    if not session:
        return

    result = await session.execute(select(ChannelFile).where(ChannelFile.id == file_id_db))
    cfile = result.scalar_one_or_none()

    if not cfile:
        await callback.answer("❌ Fayl topilmadi.", show_alert=True)
        return

    try:
        cfile.downloads += 1
        await session.commit()

        if cfile.channel_id and cfile.message_id:
            await callback.bot.forward_message(
                chat_id=callback.message.chat.id,
                from_chat_id=cfile.channel_id,
                message_id=cfile.message_id,
            )
        else:
            await callback.message.answer_document(
                document=cfile.file_id,
                caption=cfile.caption or cfile.file_name or "Fayl",
            )
        await callback.answer("✅ Fayl yuborildi!")
    except Exception as e:
        await callback.answer(f"❌ Yuborishda xatolik: {str(e)[:100]}", show_alert=True)
