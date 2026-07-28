"""Arabic locale — Hikmah AI"""
TEXTS: dict[str, str] = {
    "welcome": (
        "🤖 <b>مرحباً بك في Hikmah AI!</b>\n\n"
        "أنا مساعدك الذكي — اسألني أي شيء، اكتب نصوصاً، "
        "أنشئ صوراً، وترجم المحتوى والمزيد!\n\n"
        "📌 /help — كل الإمكانيات"
    ),
    "ai_thinking": "🤔 أفكر...",
    "processing": "⏳ جارٍ المعالجة...",
    "error_generic": "❌ حدث خطأ. يرجى المحاولة لاحقاً.",
    "limit_exceeded": (
        "❌ <b>انتهى حد الاستخدام اليومي!</b>\n\n"
        "{bar}\n\n"
        "⏰ يتجدد الحد غداً في 00:00 UTC.\n"
        "💎 احصل على Premium لزيادة الحد!"
    ),
    "banned": "🚫 لقد تم حظرك من البوت.",
    "islamic_menu": "🕌 <b>القسم الإسلامي</b>\n\nاختر من الخدمات التالية:",
    "prayer_times_header": "🕌 <b>أوقات الصلاة — {city}</b>\n📅 {date}\n\n",
    "premium_required": (
        "💎 <b>هذه الميزة متاحة فقط للمستخدمين المميزين!</b>\n\n"
        "احصل على Premium وأزل جميع القيود.\n"
        "👉 /premium"
    ),
}


def t(key: str, **kwargs) -> str:
    text = TEXTS.get(key, f"[missing: {key}]")
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
