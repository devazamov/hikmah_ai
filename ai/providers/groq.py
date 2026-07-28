"""
Hikmah AI — Groq Provider (Ultra-fast inference)
"""
from __future__ import annotations

from typing import List, Optional

from ai.base import AIResponse, BaseAIProvider, Message
from config.settings import settings
from utils.logger import logger

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqProvider(BaseAIProvider):
    name = "groq"
    available_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "llama-3.2-11b-vision-preview",
    ]

    def __init__(self) -> None:
        self._client: Optional[AsyncGroq] = None
        if not GROQ_AVAILABLE:
            logger.warning("groq not installed.")
            return
        if not settings.groq_api_key:
            logger.warning("GROQ_API_KEY not set — Groq provider disabled.")
            return
        self._client = AsyncGroq(api_key=settings.groq_api_key)
        logger.info("✅ Groq provider ready.")

    async def is_available(self) -> bool:
        return self._client is not None

    async def chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AIResponse:
        if not self._client:
            return AIResponse(
                text="",
                provider=self.name,
                model=model or "",
                success=False,
                error="Groq API kaliti o'rnatilmagan. Admin bilan bog'laning.",
            )

        _model = model or self.available_models[0]
        try:
            completion = await self._client.chat.completions.create(
                model=_model,
                messages=self._format_messages(messages),
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = completion.choices[0].message.content or ""
            usage = completion.usage
            return AIResponse(
                text=text,
                provider=self.name,
                model=_model,
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                success=True,
            )
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return AIResponse(
                text="",
                provider=self.name,
                model=_model,
                success=False,
                error=f"Groq xatosi: {str(e)[:200]}",
            )
