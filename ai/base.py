"""
Hikmah AI — Abstract AI Provider Base
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator, List, Optional


@dataclass
class Message:
    role: str  # user | assistant | system
    content: str


@dataclass
class AIResponse:
    text: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    success: bool = True
    error: Optional[str] = None


class BaseAIProvider(ABC):
    """Abstract base for all AI providers."""

    name: str = "base"
    available_models: List[str] = []

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AIResponse:
        """Send a chat completion request."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider API key is set and reachable."""
        ...

    @staticmethod
    def _format_messages(messages: List[Message]) -> List[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]
