"""
Hikmah AI — AI Service
Orchestrates AI requests with context management
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional

from ai import ai_manager, Message, AIResponse
from ai.personas.personas import get_persona
from database.models import AIUsage, User
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger


# In-memory conversation history (user_id -> messages)
_conversation_history: Dict[int, List[Message]] = {}
MAX_HISTORY = 10  # Keep last N messages


class AIService:

    @staticmethod
    def get_history(user_id: int) -> List[Message]:
        return _conversation_history.get(user_id, [])

    @staticmethod
    def add_to_history(user_id: int, role: str, content: str) -> None:
        history = _conversation_history.setdefault(user_id, [])
        history.append(Message(role=role, content=content))
        # Keep only last MAX_HISTORY messages (preserve system)
        system = [m for m in history if m.role == "system"]
        chat = [m for m in history if m.role != "system"]
        if len(chat) > MAX_HISTORY * 2:
            chat = chat[-(MAX_HISTORY * 2):]
        _conversation_history[user_id] = system + chat

    @staticmethod
    def clear_history(user_id: int) -> None:
        _conversation_history.pop(user_id, None)

    @staticmethod
    async def chat(
        session: AsyncSession,
        user: User,
        user_message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AIResponse:
        """
        Full chat with history, persona, and usage tracking.
        """
        user_id = user.telegram_id
        persona = get_persona(user.ai_persona)

        # Build messages
        messages: List[Message] = [Message(role="system", content=persona.system_prompt)]

        # Add history
        history = AIService.get_history(user_id)
        for msg in history:
            if msg.role != "system":
                messages.append(msg)

        # Add current message
        messages.append(Message(role="user", content=user_message))

        # Select provider
        _provider = provider or user.ai_provider or None
        _model = model or user.ai_model or None

        response = await ai_manager.chat(
            messages=messages,
            provider=_provider,
            model=_model,
        )

        # Update history
        AIService.add_to_history(user_id, "user", user_message)
        if response.success:
            AIService.add_to_history(user_id, "assistant", response.text)

        # Log to DB
        usage = AIUsage(
            telegram_id=user_id,
            provider=response.provider,
            model=response.model,
            feature="chat",
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            success=response.success,
            error=response.error,
        )
        session.add(usage)
        await session.commit()

        return response

    @staticmethod
    async def translate(
        text: str,
        target_lang: str,
        source_lang: str = "auto",
        user: Optional[User] = None,
    ) -> AIResponse:
        """Translate text using AI."""
        lang_names = {
            "uz": "O'zbek",
            "ar": "Arabcha",
            "en": "Inglizcha",
            "ru": "Ruscha",
            "tr": "Turk",
            "de": "Nemis",
            "fr": "Fransuz",
            "zh": "Xitoy",
        }
        target = lang_names.get(target_lang, target_lang)

        prompt = f"Quyidagi matnni {target} tiliga tarjima qil. Faqat tarjimani yoz, boshqa narsa yozma:\n\n{text}"
        messages = [
            Message(role="system", content="Sen professional tarjimonsan."),
            Message(role="user", content=prompt),
        ]
        return await ai_manager.chat(messages=messages)

    @staticmethod
    async def summarize(text: str, lang: str = "uz") -> AIResponse:
        """Summarize text in the given language."""
        prompt = (
            f"Quyidagi matnning qisqacha xulasasini O'zbek tilida chiqar. "
            f"Asosiy fikrlarni 5-7 ta band ko'rinishida ber:\n\n{text[:4000]}"
        )
        messages = [
            Message(role="system", content="Sen xulosa chiqarish mutaxassisisan."),
            Message(role="user", content=prompt),
        ]
        return await ai_manager.chat(messages=messages)

    @staticmethod
    async def solve_math(problem: str) -> AIResponse:
        """Solve mathematical problem step by step."""
        prompt = (
            f"Bu matematik masalani bosqichma-bosqich yech va tushuntir:\n\n{problem}"
        )
        messages = [
            Message(role="system", content=(
                "Sen matematik mutaxassis sifatida ishlaysan. "
                "Har qadamni tushuntir, formulalarni ko'rsat va javobni aniq yoz."
            )),
            Message(role="user", content=prompt),
        ]
        return await ai_manager.chat(messages=messages)

    @staticmethod
    async def islamic_answer(question: str) -> AIResponse:
        """Answer Islamic/religious question."""
        messages = [
            Message(role="system", content=(
                "Sen islomiy bilimlar bo'yicha mutaxassissan. "
                "Qur'on va sahih hadislar asosida javob ber. "
                "Manba ko'rsat (sura nomi, hadis kitobi). "
                "Shubhali masalalarda 'alim bilan maslahatlash' de."
            )),
            Message(role="user", content=question),
        ]
        return await ai_manager.chat(messages=messages)

    @staticmethod
    async def analyze_image_description(description: str) -> AIResponse:
        """Analyze image from description."""
        messages = [
            Message(role="system", content="Sen rasm tahlil qiluvchi AI sifatida ishlaysan."),
            Message(role="user", content=f"Bu rasmni tahlil qil: {description}"),
        ]
        return await ai_manager.chat(messages=messages)

    @staticmethod
    async def web_search_answer(query: str) -> AIResponse:
        """Answer using web search context."""
        prompt = (
            f"'{query}' haqida eng yangi va aniq ma'lumot ber. "
            "Manba va sana ko'rsat (imkon bo'lsa)."
        )
        messages = [
            Message(role="system", content=(
                "Sen internetdan ma'lumot qidiruvchi AI sifatida ishlaysan. "
                "Aniq, ishonchli va yangi ma'lumot ber."
            )),
            Message(role="user", content=prompt),
        ]
        return await ai_manager.chat(messages=messages)
