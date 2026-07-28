"""Tests for AI providers (mock-based, no real API calls)."""
import pytest
from unittest.mock import AsyncMock, patch
from ai.base import Message, AIResponse
from ai.personas.personas import get_persona, PERSONAS


def test_get_persona_default():
    p = get_persona("default")
    assert p.key == "default"
    assert p.emoji == "🤖"
    assert "Hikmah AI" in p.name


def test_get_persona_islamic():
    p = get_persona("islamic")
    assert p.key == "islamic"
    assert "Islomiy" in p.name


def test_get_persona_unknown_returns_default():
    p = get_persona("unknown_persona_xyz")
    assert p.key == "default"


def test_all_personas_have_system_prompt():
    for key, persona in PERSONAS.items():
        assert persona.system_prompt, f"Persona '{key}' has no system_prompt"
        assert len(persona.system_prompt) > 20, f"Persona '{key}' system_prompt too short"


def test_message_creation():
    msg = Message(role="user", content="Salom!")
    assert msg.role == "user"
    assert msg.content == "Salom!"


def test_ai_response_success():
    resp = AIResponse(text="Javob", provider="gemini", model="gemini-1.5-flash", success=True)
    assert resp.success is True
    assert resp.text == "Javob"


def test_ai_response_failure():
    resp = AIResponse(text="", provider="gemini", model="", success=False, error="API error")
    assert resp.success is False
    assert resp.error == "API error"
    assert resp.text == ""
