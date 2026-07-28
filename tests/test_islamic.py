"""Tests for Islamic service utilities."""
import pytest
from services.islamic_service import get_random_dua, get_random_hadith, DUAS, HADITH_POOL


def test_get_random_dua_returns_string():
    dua = get_random_dua()
    assert isinstance(dua, str)
    assert "Dua" in dua or "dua" in dua.lower()
    assert len(dua) > 10


def test_get_random_dua_has_arabic():
    dua = get_random_dua()
    # Should contain Arabic text (unicode range)
    has_arabic = any('\u0600' <= c <= '\u06ff' for c in dua)
    assert has_arabic, "Dua should contain Arabic text"


def test_get_random_hadith_returns_string():
    hadith = get_random_hadith()
    assert isinstance(hadith, str)
    assert len(hadith) > 20


def test_get_random_hadith_has_source():
    hadith = get_random_hadith()
    assert "Manba" in hadith or "manba" in hadith.lower()


def test_duas_not_empty():
    assert len(DUAS) > 0


def test_hadith_pool_not_empty():
    assert len(HADITH_POOL) > 0


def test_all_hadith_have_source():
    for h in HADITH_POOL:
        assert "source" in h
        assert h["source"]
