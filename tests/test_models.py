"""Tests for database model structure."""
import pytest
from database.models import (
    User, AIUsage, Movie, ChannelFile, PromoCode,
    SupportTicket, Note, Reminder, Broadcast, Achievement
)


def test_user_model_fields():
    """User model should have all required fields."""
    fields = [f.key for f in User.__table__.columns]
    required = [
        "telegram_id", "username", "full_name", "is_premium",
        "is_banned", "daily_requests_used", "points", "streak",
        "referral_code", "language", "ai_provider", "ai_model",
    ]
    for field in required:
        assert field in fields, f"Missing field: {field}"


def test_movie_model_fields():
    fields = [f.key for f in Movie.__table__.columns]
    assert "code" in fields
    assert "title" in fields
    assert "file_id" in fields
    assert "is_active" in fields


def test_promo_code_model_fields():
    fields = [f.key for f in PromoCode.__table__.columns]
    assert "code" in fields
    assert "max_uses" in fields
    assert "used_count" in fields


def test_note_model_fields():
    fields = [f.key for f in Note.__table__.columns]
    assert "telegram_id" in fields
    assert "title" in fields
    assert "content" in fields


def test_reminder_model_fields():
    fields = [f.key for f in Reminder.__table__.columns]
    assert "remind_at" in fields
    assert "is_sent" in fields
