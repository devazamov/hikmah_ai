# 🤖 Hikmah AI — Professional Telegram AI Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![aiogram](https://img.shields.io/badge/aiogram-3.x-green?logo=telegram)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange?logo=firebase)
![License](https://img.shields.io/badge/License-MIT-yellow)

**O'zbekiston uchun yaratilgan professional Telegram AI platformasi**  
*Islamic AI · Movie Bot · Video Download · Admin Panel · Gamification*

</div>

---

## ✨ Imkoniyatlar (50+ Funksiya)

### 🤖 AI Chat
- Google Gemini, Groq, OpenRouter (100+ model)
- Uzoq suhbat xotirasi (Context window)
- 8 ta AI persona (Islomiy ustoz, Tabib, Huquqshunos, Qori...)
- AI tarjimon (O'zbek ↔ Arabcha ↔ Inglizcha ↔ Ruscha)
- Matn va YouTube video xulosa qilish
- Matematik masalalar yechish
- Internetdan qidirib javob berish
- AI rasm tahlili (Vision)

### 🕌 Islomiy AI Bot
- Qur'on oyatlarini chiqarish (arabcha + tarjima)
- Namoz vaqtlari (har shahar uchun)
- Kunlik dua va hadislar
- Islomiy savol-javob
- Qibla yo'nalishi
- Islomiy takvim
- Qori bot (Qur'on audio)

### 🎬 Kino Bot
- Kod orqali kino olish (MV001 ...)
- Kino qidiruv (nomi bo'yicha)
- Islomiy kinolar bo'limi
- Admin orqali kino qo'shish

### 📥 Video/Media
- YouTube, Instagram, TikTok, Facebook yuklab olish (yt-dlp)
- Ovoz → Matn (Whisper)
- Matn → Ovoz (TTS)
- PDF bilan suhbat (RAG)
- AI rasm yaratish
- QR kod generatori
- Fayl formatlari o'zgartirish

### 🛠️ Vositalar
- 🌤️ Ob-havo (OpenWeatherMap)
- 💱 Valyuta kurslari (real vaqt)
- 🔢 Ilmiy kalkulyator
- 📓 Shaxsiy eslatmalar
- ⏰ Eslatmalar va taymerlar
- 🔗 URL qisqartirish
- 📊 So'rovnoma yaratish

### 👥 Foydalanuvchi Tizimi
- Avtomatik ro'yxatdan o'tish
- Kunlik AI limit (Oddiy: 50, Pro: 150, Premium: 300, Ultra: Cheksiz)
- Kunlik limit progress bar: `██████░░░░ 30/50`
- Referral tizimi (+10 bonus so'rov/do'st)
- Promo kod tizimi
- Premium obuna rejalari (Basic/Pro/Ultra)

### 🎮 Gamifikatsiya
- ⭐ Ball tizimi (AI so'rov = +2 ball, referral = +50 ball)
- 🏅 Darajalar (Yangi boshlovchi → Grand Master)
- 🏆 Yutuqlar/Badgelar (10+ tur)
- 🔥 Kunlik kirish seriyasi (Streak)
- 🎁 Kunlik bonus (+ball seriya bilan ortadi)
- 📊 Global reyting (Top foydalanuvchilar)

### 🛡️ Admin Panel
- 📊 Real vaqt statistika (bugun/hafta/oy/jami)
- 📢 Broadcast (matn, rasm, video, forward, scheduled)
- 💎 Premium berish/olish
- 🚫 Ban/Unban
- 🎟️ Promo kod yaratish
- 🎬 Kino qo'shish/o'chirish
- 📺 Kanal boshqaruvi
- 🔑 API kalitlar holati
- 📤 CSV export (1000+ foydalanuvchi)
- 📋 Log fayllarni ko'rish
- 🤖 AI provayder tanlash

### 🔒 Xavfsizlik
- Rate limiting (30 xabar/daqiqa)
- Flood protection (3 xabar/soniya)
- Admin permission tizimi
- Majburiy obuna tekshiruvi
- Secure API key management (.env)
- Encrypted logging

---

## 📋 Tezkor Boshlash

### 1. Talablar
```
Python 3.12+
pip
```

### 2. O'rnatish
```bash
git clone https://github.com/yourusername/hikmah-ai.git
cd hikmah-ai
pip install -r requirements.txt
```

### 3. Sozlash
```bash
cp .env.example .env
nano .env  # API kalitlarni kiriting
```

### 4. Ishga tushirish
```bash
python main.py
```

---

## 🔑 Kerakli Environment Variables

| O'zgaruvchi | Majburiy | Tavsif |
|---|---|---|
| `BOT_TOKEN` | ✅ | [@BotFather](https://t.me/BotFather) dan oling |
| `ADMIN_IDS` | ✅ | Admin Telegram ID lari (vergul bilan) |
| `GEMINI_API_KEY` | ⚠️ | [Google AI Studio](https://aistudio.google.com/) |
| `GROQ_API_KEY` | ⚠️ | [Groq Console](https://console.groq.com/) |
| `OPENROUTER_API_KEY` | ⚠️ | [OpenRouter](https://openrouter.ai/) |
| `WEATHER_API_KEY` | ➕ | [OpenWeatherMap](https://openweathermap.org/api) (bepul) |
| `FIREBASE_PROJECT_ID` | ➕ | Firebase Console |
| `DATABASE_URL` | ✅ | SQLite (default) yoki PostgreSQL |

> ⚠️ Kamida **bitta** AI provayder API kaliti kerak!

---

## 🔑 API Kalitlarni Qayerdan Olish

### Google Gemini (BEPUL)
1. [aistudio.google.com](https://aistudio.google.com/) ga kiring
2. "Get API key" → API kalitni nusxalang
3. `.env` ga kiriting: `GEMINI_API_KEY=your_key`

### Groq (BEPUL, ultra-tez)
1. [console.groq.com](https://console.groq.com/) ga kiring
2. "API Keys" → "Create API Key"
3. `.env` ga kiriting: `GROQ_API_KEY=your_key`

### OpenRouter (ko'p modelli)
1. [openrouter.ai](https://openrouter.ai/) ga kiring
2. "Keys" → "Create Key"
3. `.env` ga kiriting: `OPENROUTER_API_KEY=your_key`

### Firebase (ixtiyoriy)
1. [Firebase Console](https://console.firebase.google.com/) → Loyiha yarating
2. "Project Settings" → "Service Accounts" → "Generate new private key"
3. JSON faylidagi ma'lumotlarni `.env` ga kiriting

### OpenWeatherMap (bepul, ob-havo)
1. [openweathermap.org](https://openweathermap.org/api) → ro'yxatdan o'ting
2. "API Keys" bo'limidan kalitni oling
3. `.env` ga kiriting: `WEATHER_API_KEY=your_key`

---

## 🐳 Docker bilan Ishlatish

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f hikmah_ai

# Stop
docker-compose down
```

---

## ☁️ Deploy (Render.com)

1. GitHub ga push qiling
2. [render.com](https://render.com/) → "New Web Service"
3. Repository tanlang
4. Build command: `pip install -r requirements.txt`
5. Start command: `python main.py`
6. Environment variables ni kiriting

---

## ☁️ Deploy (Replit)

1. Replit.com ga import qiling
2. Secrets bo'limida environment variables kiriting
3. `main.py` ni ishga tushiring

---

## 📁 Loyiha Strukturasi

```
hikmah_ai/
├── main.py                 # Entry point
├── config/
│   └── settings.py         # Barcha sozlamalar
├── bot/
│   ├── handlers/           # Message handlers
│   │   ├── start.py
│   │   ├── ai_chat.py      # Asosiy AI chat
│   │   ├── profile.py
│   │   ├── settings.py
│   │   ├── islamic.py      # Islomiy funksiyalar
│   │   ├── tools.py        # Vositalar
│   │   ├── movies.py       # Kino bot
│   │   └── premium.py
│   ├── admin/              # Admin panel
│   │   ├── panel.py
│   │   ├── broadcast.py
│   │   └── movies_admin.py
│   ├── middlewares/        # Auth, rate limit, logging
│   ├── filters/            # Admin, premium
│   ├── keyboards/          # All keyboards
│   └── states/             # FSM states
├── ai/
│   ├── base.py             # Abstract provider
│   ├── providers/          # Gemini, Groq, OpenRouter
│   └── personas/           # AI rollar
├── database/
│   ├── models.py           # SQLAlchemy models
│   ├── sqlite.py           # DB engine
│   └── firebase.py         # Firestore
├── services/
│   ├── user_service.py     # Foydalanuvchi logikasi
│   ├── ai_service.py       # AI orchestration
│   ├── channel_service.py  # Obuna tekshiruvi
│   ├── islamic_service.py  # Qur'on, namoz vaqtlari
│   ├── video_service.py    # yt-dlp
│   ├── weather_service.py
│   ├── currency_service.py
│   └── scheduler.py        # APScheduler
├── locales/
│   ├── uz.py               # O'zbek tili
│   └── ar.py               # Arabcha
└── utils/
    ├── helpers.py
    ├── security.py
    └── logger.py
```

---

## 🧪 Testlar

```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

---

## 📞 Yordam

- Bot: [@aiHikmah_bot](https://t.me/aiHikmah_bot)
- Support: [@HikmahSupport](https://t.me/HikmahSupport)

---

<div align="center">
Made with ❤️ for Uzbekistan | بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ
</div>
