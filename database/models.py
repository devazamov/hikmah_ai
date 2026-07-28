"""
Hikmah AI — SQLAlchemy Models (SQLite/PostgreSQL)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128), default="")
    first_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="uz")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # basic|pro|ultra
    premium_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Limits
    daily_requests_used: Mapped[int] = mapped_column(Integer, default=0)
    daily_reset_date: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    bonus_requests: Mapped[int] = mapped_column(Integer, default=0)

    # Gamification
    points: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_daily_bonus: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)

    # Referral
    referral_code: Mapped[Optional[str]] = mapped_column(String(12), unique=True, nullable=True)
    referred_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    referral_count: Mapped[int] = mapped_column(Integer, default=0)

    # Settings
    ai_provider: Mapped[str] = mapped_column(String(32), default="gemini")
    ai_model: Mapped[str] = mapped_column(String(64), default="gemini-1.5-flash")
    ai_persona: Mapped[str] = mapped_column(String(32), default="default")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} @{self.username}>"


class AIUsage(Base):
    __tablename__ = "ai_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    provider: Mapped[str] = mapped_column(String(32))
    model: Mapped[str] = mapped_column(String(64))
    feature: Mapped[str] = mapped_column(String(32), default="chat")  # chat|image|voice|translate|...
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(256))
    title_uz: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    genre: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    file_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    thumbnail_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    is_islamic: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ChannelFile(Base):
    __tablename__ = "channel_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger)
    message_id: Mapped[int] = mapped_column(BigInteger)
    file_id: Mapped[str] = mapped_column(String(512))
    file_unique_id: Mapped[str] = mapped_column(String(256), unique=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    file_type: Mapped[str] = mapped_column(String(32))  # pdf|video|audio|zip|apk|doc|image
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    premium_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # basic|pro|ultra
    bonus_requests: Mapped[int] = mapped_column(Integer, default=0)
    bonus_points: Mapped[int] = mapped_column(Integer, default=0)
    max_uses: Mapped[int] = mapped_column(Integer, default=1)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    subject: Mapped[str] = mapped_column(String(256))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="open")  # open|pending|closed
    admin_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    title: Mapped[str] = mapped_column(String(128))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    text: Mapped[str] = mapped_column(Text)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Broadcast(Base):
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    media_file_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    total_users: Mapped[int] = mapped_column(Integer, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending|running|done|failed
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    badge: Mapped[str] = mapped_column(String(64))  # first_message|streak_7|...
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
