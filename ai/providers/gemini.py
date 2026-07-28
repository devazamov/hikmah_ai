"""
Hikmah AI — Google Gemini Provider
"""
from __future__ import annotations

from typing import List, Optional

from ai.base import AIResponse, BaseAIProvider, Message
from config.settings import settings
from utils.logger import logger

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiProvider(BaseAIProvider):
    name = "gemini"
    available_models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "gemini-pro",
    ]

    def __init__(self) -> None:
        self._configured = False
        if not GEMINI_AVAILABLE:
            logger.warning("google-generativeai not installed.")
            return
        if not settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set — Gemini provider disabled.")
            return
        genai.configure(api_key=settings.gemini_api_key)
        self._configured = True
        logger.info("✅ Gemini provider ready.")

    async def is_available(self) -> bool:
        return self._configured

    async def chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AIResponse:
        if not self._configured:
            return AIResponse(
                text="",
                provider=self.name,
                model=model or "",
                success=False,
                error="Gemini API kaliti o'rnatilmagan. Admin bilan bog'laning.",
            )

        _model = model or settings.default_ai_model
        if _model not in self.available_models:
            _model = self.available_models[0]

        try:
            client = genai.GenerativeModel(
                model_name=_model,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            # Build history for Gemini format
            history = []
            system_prompt = None
            for msg in messages:
                if msg.role == "system":
                    system_prompt = msg.content
                elif msg.role == "user":
                    history.append({"role": "user", "parts": [msg.content]})
                elif msg.role == "assistant":
                    history.append({"role": "model", "parts": [msg.content]})

            if system_prompt:
                client = genai.GenerativeModel(
                    model_name=_model,
                    system_instruction=system_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )

            # Last user message
            last_user = next(
                (m.content for m in reversed(messages) if m.role == "user"), ""
            )
            chat_session = client.start_chat(history=history[:-1] if history else [])
            response = await chat_session.send_message_async(last_user)

            text = response.text or ""
            return AIResponse(
                text=text,
                provider=self.name,
                model=_model,
                prompt_tokens=response.usage_metadata.prompt_token_count if hasattr(response, "usage_metadata") else 0,
                completion_tokens=response.usage_metadata.candidates_token_count if hasattr(response, "usage_metadata") else 0,
                success=True,
            )

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return AIResponse(
                text="",
                provider=self.name,
                model=_model,
                success=False,
                error=f"Gemini xatosi: {str(e)[:200]}",
            )
