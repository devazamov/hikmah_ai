"""Tests for helper utilities."""
import pytest
from utils.helpers import (
    progress_bar, generate_referral_code, generate_promo_code,
    format_number, truncate, level_info, get_limit_text,
)


def test_progress_bar_empty():
    assert progress_bar(0, 50) == "░░░░░░░░░░ 0/50"


def test_progress_bar_full():
    assert progress_bar(50, 50) == "██████████ 50/50"


def test_progress_bar_half():
    bar = progress_bar(25, 50)
    assert "25/50" in bar
    assert "█" in bar
    assert "░" in bar


def test_generate_referral_code_length():
    code = generate_referral_code(123456789)
    assert len(code) == 8
    assert code.isupper()


def test_generate_promo_code_length():
    code = generate_promo_code(10)
    assert len(code) == 10


def test_format_number():
    assert format_number(1000000) == "1,000,000"
    assert format_number(0) == "0"


def test_truncate():
    long_text = "a" * 300
    result = truncate(long_text, 200)
    assert len(result) <= 203  # 200 + "..."
    assert result.endswith("...")


def test_truncate_short():
    short = "Hello"
    assert truncate(short, 200) == "Hello"


def test_level_info_beginner():
    info = level_info(0)
    assert "Yangi boshlovchi" in info["name"]


def test_level_info_expert():
    info = level_info(5000)
    assert "Ekspert" in info["name"]


def test_get_limit_text_normal():
    text = get_limit_text(20, 50)
    assert "20/50" in text


def test_get_limit_text_exceeded():
    text = get_limit_text(50, 50)
    assert "tugadi" in text.lower()
