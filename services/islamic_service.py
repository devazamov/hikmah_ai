"""
Hikmah AI — Islamic Services
Quran, Prayer Times, Hadith, Dua
"""
from __future__ import annotations

import random
from datetime import datetime
from typing import Optional

import aiohttp

from config.settings import settings
from utils.logger import logger

QURAN_API = "https://api.alquran.cloud/v1"
ALADHAN_API = "https://api.aladhan.com/v1"

# Random Islamic duas for daily messages
DUAS = [
    ("رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ",
     "Parvardigorо, bizga dunyoda ham, oxiratda ham yaxshilik ber va bizni do'zax azobidan saqlа"),
    ("رَبِّ زِدْنِي عِلْمًا",
     "Parvardigor, bilimimni oshir"),
    ("اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ",
     "Allohim, men qayg'u va g'amdan Senga suyonaman"),
    ("سُبْحَانَ اللَّهِ وَبِحَمْدِهِ",
     "Allohni hamd bilan ulug'layman"),
    ("لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ",
     "Allohdan boshqa iloh yo'q, U yakkа, sherikи yo'q"),
]

HADITH_POOL = [
    {
        "text": "Sizlarning eng yaxshingiz Qur'onni o'rganuvchi va o'rgatuvchidir.",
        "source": "Sahih Buxoriy, 5027",
        "arabic": "خَيْرُكُمْ مَنْ تَعَلَّمَ الْقُرْآنَ وَعَلَّمَهُ",
    },
    {
        "text": "Musilmon kishining eng yaxshi sadaqasi ilm o'rganib, uni o'z birodariga o'rgatishidir.",
        "source": "Ibn Moja",
        "arabic": "أَفْضَلُ الصَّدَقَةِ أَنْ يَتَعَلَّمَ الْمَرْءُ عِلْمًا ثُمَّ يُعَلِّمَهُ أَخَاهُ",
    },
    {
        "text": "Har bir muslim uchun ilm olish farzdir.",
        "source": "Ibn Moja, 224",
        "arabic": "طَلَبُ الْعِلْمِ فَرِيضَةٌ عَلَى كُلِّ مُسْلِمٍ",
    },
    {
        "text": "Odamlarning eng yomoni — bilimsizligini bilmaydiganlaridir.",
        "source": "Hikmat",
        "arabic": "",
    },
    {
        "text": "Kimki ilm talab qilib bir yo'lga kirsa, Allah uni jannat yo'liga kiritadi.",
        "source": "Sahih Muslim, 2699",
        "arabic": "مَنْ سَلَكَ طَرِيقًا يَلْتَمِسُ فِيهِ عِلْمًا سَهَّلَ اللَّهُ لَهُ بِهِ طَرِيقًا إِلَى الْجَنَّةِ",
    },
]

PRAYER_NAMES_UZ = {
    "Fajr": "🌅 Bomdod",
    "Sunrise": "🌄 Quyosh chiqishi",
    "Dhuhr": "🌞 Peshin",
    "Asr": "🌇 Asr",
    "Maghrib": "🌆 Shom",
    "Isha": "🌙 Xufton",
    "Midnight": "🌃 Yarim tun",
    "Lastthird": "🌌 Kecha so'nggi uchdan biri",
}


async def get_quran_ayah(surah: int, ayah: int) -> Optional[str]:
    """Get Quran ayah with Arabic text and translation."""
    try:
        async with aiohttp.ClientSession() as session:
            # Arabic
            arabic_url = f"{QURAN_API}/ayah/{surah}:{ayah}/ar.alafasy"
            # Translation (Uzbek if available, else English)
            trans_url = f"{QURAN_API}/ayah/{surah}:{ayah}/en.asad"

            async with session.get(arabic_url, timeout=aiohttp.ClientTimeout(total=10)) as r1:
                ar_data = await r1.json()
            async with session.get(trans_url, timeout=aiohttp.ClientTimeout(total=10)) as r2:
                tr_data = await r2.json()

        ar_ayah = ar_data.get("data", {})
        tr_ayah = tr_data.get("data", {})

        arabic_text = ar_ayah.get("text", "")
        translation = tr_ayah.get("text", "")
        surah_name = ar_ayah.get("surah", {}).get("englishName", "")
        surah_name_ar = ar_ayah.get("surah", {}).get("name", "")

        return (
            f"📖 <b>Qur'on — {surah_name} ({surah_name_ar})</b>\n"
            f"Sura: {surah}, Oyat: {ayah}\n\n"
            f"<b>Arabic:</b>\n{arabic_text}\n\n"
            f"<b>Tarjima (Inglizcha):</b>\n{translation}"
        )
    except Exception as e:
        logger.error(f"Quran API error: {e}")
        return "❌ Qur'on ma'lumotini olishda xatolik. Keyinroq urinib ko'ring."


async def get_prayer_times(city: str, country: str = "UZ") -> Optional[str]:
    """Get prayer times for a city."""
    try:
        date = datetime.now().strftime("%d-%m-%Y")
        params = {
            "city": city,
            "country": country,
            "method": 4,  # Umm Al-Qura University, Makkah
        }
        async with aiohttp.ClientSession() as session:
            url = f"{ALADHAN_API}/timingsByCity/{date}"
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        timings = data.get("data", {}).get("timings", {})
        date_info = data.get("data", {}).get("date", {}).get("readable", date)

        lines = [f"🕌 <b>Namoz vaqtlari — {city}</b>\n📅 {date_info}\n"]
        for eng, uz in PRAYER_NAMES_UZ.items():
            if eng in timings:
                lines.append(f"{uz}: <b>{timings[eng]}</b>")

        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Prayer time error: {e}")
        return "❌ Namoz vaqtlarini olishda xatolik."


def get_random_dua() -> str:
    arabic, translation = random.choice(DUAS)
    return (
        f"🤲 <b>Dua</b>\n\n"
        f"<i>{arabic}</i>\n\n"
        f"📜 <b>Tarjima:</b>\n{translation}"
    )


def get_random_hadith() -> str:
    h = random.choice(HADITH_POOL)
    text = (
        f"📿 <b>Hadis</b>\n\n"
        f"<i>{h['text']}</i>\n\n"
        f"📚 <b>Manba:</b> {h['source']}"
    )
    if h.get("arabic"):
        text = f"<code>{h['arabic']}</code>\n\n" + text
    return text


ISLAMIC_CALENDAR_MONTHS = [
    "Muharram", "Safar", "Rabi ul-Avval", "Rabi ul-Oxir",
    "Jumad ul-Avval", "Jumad ul-Oxir", "Rajab", "Sha'bon",
    "Ramazon", "Shavvol", "Zul-Qa'da", "Zul-Hijja"
]
