"""
Hikmah AI — OpenRouter Provider (100+ models)
"""
from __future__ import annotations

from typing import List, Optional

from ai.base import AIResponse, BaseAIProvider, Message
from config.settings import settings
from utils.logger import logger

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenRouterProvider(BaseAIProvider):
    name = "openrouter"
    available_models = [
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "anthropic/claude-3-haiku",
        "anthropic/claude-3.5-sonnet",
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemini-flash-1.5",
        "mistralai/mistral-7b-instruct:free",
        "deepseek/deepseek-chat",
    ]

    def __init__(self) -> None:
        self._client: Optional[AsyncOpenAI] = None
        if not OPENAI_AVAILABLE:
            logger.warning("openai package not installed.")
            return
        if not settings.openrouter_api_key:
            logger.warning("OPENROUTER_API_KEY not set — OpenRouter disabled.")
            return
        self._client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        logger.info("✅ OpenRouter provider ready.")

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
                error="OpenRouter API kaliti o'rnatilmagan. Admin bilan bog'laning.",
            )

        _model = model or self.available_models[0]
        try:
            completion = await self._client.chat.completions.create(
                model=_model,
                messages=self._format_messages(messages),
                temperature=temperature,
                max_tokens=max_tokens,
                extra_headers={
                    "HTTP-Referer": "https://t.me/aiHikmah_bot",
                    "X-Title": "Hikmah AI",
                },
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
            logger.error(f"OpenRouter error: {e}")
            return AIResponse(
                text="",
                provider=self.name,
                model=_model,
                success=False,
                error=f"OpenRouter xatosi: {str(e)[:200]}",
            )
