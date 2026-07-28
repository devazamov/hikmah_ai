"""O'zbek tili — Hikmah AI"""
from __future__ import annotations

TEXTS: dict[str, str] = {
    # ── General ──────────────────────────────────
    "welcome": (
        "🤖 <b>Hikmah AI</b> ga xush kelibsiz!\n\n"
        "Men sizning aqlli yordamchingizman — "
        "savol bering, matn yozing, rasm yarat, tarjima qiling va ko'p narsalar!\n\n"
        "📌 /help — barcha imkoniyatlar"
    ),
    "help_text": (
        "📚 <b>Hikmah AI — Imkoniyatlar</b>\n\n"
        "🤖 <b>AI Chat</b>\n"
        "  • Istalgan savolga javob\n"
        "  • Matn yozishda yordam\n"
        "  • Kod yozish va tushuntirish\n\n"
        "🕌 <b>Islomiy AI</b>\n"
        "  • Qur'on oyatlari va tafsir\n"
        "  • Hadislar\n"
        "  • Namoz vaqtlari\n"
        "  • Dua va zikrlar\n\n"
        "🎨 <b>Media</b>\n"
        "  • Rasm yaratish\n"
        "  • Ovozni matnga o'girish\n"
        "  • Video yuklab olish\n"
        "  • PDF bilan suhbat\n\n"
        "📊 <b>Vositalar</b>\n"
        "  • Ob-havo\n"
        "  • Valyuta kurslari\n"
        "  • Kalkulyator\n"
        "  • QR kod\n\n"
        "🎮 <b>O'yin & Reyting</b>\n"
        "  • Ball tizimi\n"
        "  • Darajalar\n"
        "  • Kundalikling seriya\n\n"
        "💎 <b>Premium</b> — /premium"
    ),
    "profile_text": (
        "👤 <b>Profilingiz</b>\n\n"
        "🆔 ID: <code>{user_id}</code>\n"
        "👤 Ism: <b>{full_name}</b>\n"
        "📱 Username: @{username}\n"
        "📅 Ro'yxatdan o'tgan: <b>{join_date}</b>\n"
        "🌐 Til: <b>{language}</b>\n\n"
        "💎 Holat: <b>{status}</b>\n"
        "⭐ Ball: <b>{points}</b>\n"
        "{level_progress}\n\n"
        "🤖 <b>AI limiti (bugun):</b>\n"
        "<code>{limit_bar}</code>\n\n"
        "🔥 Seriya: <b>{streak} kun</b>\n"
        "👥 Referallar: <b>{referrals}</b>\n"
        "📊 Jami so'rovlar: <b>{total_requests}</b>"
    ),
    "no_subscription": (
        "❌ <b>Majburiy obuna!</b>\n\n"
        "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n\n"
        "{channels}\n\n"
        "✅ Obuna bo'lgandan so'ng /start bosing."
    ),
    "limit_exceeded": (
        "❌ <b>Bugungi AI limiti tugadi!</b>\n\n"
        "{bar}\n\n"
        "⏰ Limit ertaga <b>00:00 UTC</b> da yangilanadi.\n\n"
        "💎 <b>Premium</b> olib limitni oshiring!\n"
        "👇 /premium buyrug'ini bosing"
    ),
    "rate_limited": "⚠️ Juda tez xabar yuboryapsiz. {retry} soniyadan keyin urinib ko'ring.",
    "error_generic": "❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.",
    "ai_thinking": "🤔 O'ylayapman...",
    "processing": "⏳ Ishlab chiqilmoqda...",
    "premium_required": (
        "💎 <b>Bu funksiya faqat Premium foydalanuvchilar uchun!</b>\n\n"
        "Premium oling va barcha cheklovlarni olib tashlang.\n"
        "👉 /premium"
    ),
    "banned": "🚫 Siz botdan bloklangansiz. Murojaat: @HikmahSupport",
    "settings_text": (
        "⚙️ <b>Sozlamalar</b>\n\n"
        "🌐 Til: <b>{language}</b>\n"
        "🤖 AI model: <b>{ai_model}</b>\n"
        "🔔 Bildirishnomalar: <b>{notifications}</b>\n"
        "🤖 AI persona: <b>{persona}</b>"
    ),
    "premium_text": (
        "💎 <b>Hikmah AI Premium</b>\n\n"
        "✅ Kuniga <b>300 ta</b> AI so'rov\n"
        "✅ Barcha AI modellar\n"
        "✅ AI rasm yaratish\n"
        "✅ PDF bilan suhbat\n"
        "✅ Ovoz → Matn (Whisper)\n"
        "✅ Video yuklab olish\n"
        "✅ Ustuvor xizmat\n\n"
        "📦 <b>Rejalar:</b>\n"
        "🥉 Basic — 1 oy\n"
        "🥈 Pro — 1 oy (ko'proq limit)\n"
        "🥇 Ultra — 1 oy (cheksiz)\n\n"
        "🎟️ Promo kod: /promo"
    ),
    "referral_text": (
        "👥 <b>Referral tizimi</b>\n\n"
        "🔗 Sizning havolangiz:\n"
        "<code>https://t.me/{bot_username}?start={ref_code}</code>\n\n"
        "📊 Statistika:\n"
        "👥 Taklif qilinganlar: <b>{invited}</b>\n"
        "⭐ Bonus so'rovlar: <b>{bonus}</b>\n\n"
        "💡 Har bir taklif qilingan foydalanuvchi uchun\n"
        "<b>{bonus_per_ref} ta</b> qo'shimcha AI so'rov olasiz!"
    ),
    "daily_bonus": (
        "🎁 <b>Kunlik bonus!</b>\n\n"
        "Bugun ham keldingiz! 🔥\n"
        "🎉 +{bonus} ball qo'shildi!\n"
        "🔥 Seriya: <b>{streak} kun</b>"
    ),
    # ── Islamic ──────────────────────────────────
    "islamic_menu": (
        "🕌 <b>Islomiy Bo'lim</b>\n\n"
        "Quyidagi xizmatlardan foydalaning:"
    ),
    "prayer_times_header": "🕌 <b>Namoz vaqtlari — {city}</b>\n📅 {date}\n\n",
    # ── Movies ───────────────────────────────────
    "movie_menu": (
        "🎬 <b>Kino Bot</b>\n\n"
        "Kod orqali kino oling yoki qidiring.\n\n"
        "📌 Kod yuboring yoki qidiruv tugmasini bosing."
    ),
    "movie_not_found": "❌ Bu kodda kino topilmadi. Boshqa kod kiriting.",
    # ── Admin ─────────────────────────────────────
    "admin_panel": "🛡️ <b>Admin Panel</b>\n\nQuyidagi bo'limlardan birini tanlang:",
}


def t(key: str, **kwargs) -> str:
    """Get translated text with format substitution."""
    text = TEXTS.get(key, f"[missing: {key}]")
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
