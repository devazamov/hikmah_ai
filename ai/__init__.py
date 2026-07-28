"""
Hikmah AI — AI Module
Manages providers, routing, and feature dispatch
"""
from __future__ import annotations

from typing import Dict, List, Optional

from ai.base import AIResponse, BaseAIProvider, Message
from ai.providers.gemini import GeminiProvider
from ai.providers.groq import GroqProvider
from ai.providers.openrouter import OpenRouterProvider
from config.settings import settings
from utils.logger import logger


class AIManager:
    """Central manager — selects provider and dispatches requests."""

    def __init__(self) -> None:
        self._providers: Dict[str, BaseAIProvider] = {}
        self._init_providers()

    def _init_providers(self) -> None:
        for cls in [GeminiProvider, GroqProvider, OpenRouterProvider]:
            try:
                p = cls()
                self._providers[p.name] = p
            except Exception as e:
                logger.error(f"Provider init failed {cls.__name__}: {e}")

    def get_provider(self, name: Optional[str] = None) -> BaseAIProvider:
        name = name or settings.default_ai_provider
        if name in self._providers:
            return self._providers[name]
        # Fallback chain
        for fallback in ["gemini", "groq", "openrouter"]:
            if fallback in self._providers:
                logger.warning(f"Provider '{name}' unavailable, falling back to '{fallback}'")
                return self._providers[fallback]
        raise RuntimeError("No AI provider available. Check API keys in .env")

    async def chat(
        self,
        messages: List[Message],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AIResponse:
        p = self.get_provider(provider)
        return await p.chat(messages, model=model, temperature=temperature, max_tokens=max_tokens)

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())


# Singleton
ai_manager = AIManager()

__all__ = ["ai_manager", "AIManager", "Message", "AIResponse", "BaseAIProvider"]
