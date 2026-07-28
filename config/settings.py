"""
Hikmah AI — Global Settings
Pydantic-based configuration management
"""
from __future__ import annotations

import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Telegram ──────────────────────────────────────────
    bot_token: str
    bot_username: str = "aiHikmah_bot"
    admin_ids: str = ""

    @property
    def admin_ids_list(self) -> List[int]:
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]

    # ── AI Providers ─────────────────────────────────────
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    default_ai_provider: str = "gemini"
    default_ai_model: str = "gemini-1.5-flash"

    # ── Firebase ─────────────────────────────────────────
    firebase_project_id: Optional[str] = None
    firebase_private_key_id: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_client_email: Optional[str] = None
    firebase_client_id: Optional[str] = None

    @property
    def firebase_enabled(self) -> bool:
        return all([
            self.firebase_project_id,
            self.firebase_private_key,
            self.firebase_client_email,
        ])

    # ── Database ─────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./hikmah_ai.db"

    # ── Redis ─────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    use_redis: bool = False

    # ── Webhook ───────────────────────────────────────────
    webhook_host: Optional[str] = None
    webhook_path: str = "/webhook"
    webhook_secret: Optional[str] = None

    # ── FastAPI ───────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change-me-in-production"

    # ── External APIs ─────────────────────────────────────
    weather_api_key: Optional[str] = None
    currency_api_key: Optional[str] = None
    news_api_key: Optional[str] = None

    # ── Limits ────────────────────────────────────────────
    free_daily_limit: int = 50
    premium_daily_limit: int = 300
    pro_daily_limit: int = 150

    # ── Bot Settings ──────────────────────────────────────
    bot_mode: str = "polling"
    debug: bool = False
    log_level: str = "INFO"
    timezone: str = "Asia/Tashkent"

    # ── Channels ──────────────────────────────────────────
    required_channels: str = ""
    subscription_check_enabled: bool = True

    @property
    def required_channels_list(self) -> List[int]:
        return [int(x.strip()) for x in self.required_channels.split(",") if x.strip()]

    # ── Referral ──────────────────────────────────────────
    referral_bonus_requests: int = 10

    # ── Rate Limiting ─────────────────────────────────────
    rate_limit_messages: int = 30
    rate_limit_window: int = 60

    # ── Islamic ───────────────────────────────────────────
    quran_api_url: str = "https://api.alquran.cloud/v1"
    prayer_time_api: str = "https://api.aladhan.com/v1"


# Singleton
settings = Settings()
