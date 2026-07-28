"""
Hikmah AI — Security Utilities
Rate limiting, flood protection, admin checks
"""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, Tuple

from config.settings import settings


class RateLimiter:
    """Simple in-memory rate limiter (per user)."""

    def __init__(self, max_calls: int = 30, window: int = 60):
        self.max_calls = max_calls
        self.window = window
        self._calls: Dict[int, list] = defaultdict(list)

    def is_allowed(self, user_id: int) -> Tuple[bool, int]:
        """
        Returns (allowed: bool, retry_after: int).
        retry_after = 0 if allowed.
        """
        now = time.time()
        history = self._calls[user_id]
        # Remove old calls outside window
        self._calls[user_id] = [t for t in history if now - t < self.window]
        if len(self._calls[user_id]) >= self.max_calls:
            oldest = self._calls[user_id][0]
            retry_after = int(self.window - (now - oldest)) + 1
            return False, retry_after
        self._calls[user_id].append(now)
        return True, 0


class FloodProtection:
    """Detect and block flood messages (too fast)."""

    def __init__(self, max_per_second: int = 3):
        self.max_per_second = max_per_second
        self._timestamps: Dict[int, list] = defaultdict(list)

    def is_flood(self, user_id: int) -> bool:
        now = time.time()
        history = self._timestamps[user_id]
        self._timestamps[user_id] = [t for t in history if now - t < 1.0]
        if len(self._timestamps[user_id]) >= self.max_per_second:
            return True
        self._timestamps[user_id].append(now)
        return False


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids_list


# Singletons
rate_limiter = RateLimiter(
    max_calls=settings.rate_limit_messages,
    window=settings.rate_limit_window,
)
flood_protection = FloodProtection()
