"""Tests for security utilities."""
import pytest
from utils.security import RateLimiter, FloodProtection


def test_rate_limiter_allows_within_limit():
    rl = RateLimiter(max_calls=5, window=60)
    for _ in range(5):
        allowed, retry = rl.is_allowed(999)
        assert allowed


def test_rate_limiter_blocks_over_limit():
    rl = RateLimiter(max_calls=3, window=60)
    for _ in range(3):
        rl.is_allowed(888)
    allowed, retry = rl.is_allowed(888)
    assert not allowed
    assert retry > 0


def test_flood_protection_normal():
    fp = FloodProtection(max_per_second=5)
    for _ in range(4):
        assert not fp.is_flood(777)


def test_flood_protection_detects_flood():
    fp = FloodProtection(max_per_second=2)
    fp.is_flood(555)
    fp.is_flood(555)
    assert fp.is_flood(555)
