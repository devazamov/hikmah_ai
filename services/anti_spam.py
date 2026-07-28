"""
Hikmah AI — Anti-Spam & Auto-Moderation Service
AI-powered spam detection
"""
from __future__ import annotations

import re
from typing import Optional

SPAM_PATTERNS = [
    r"(earn|make)\s*\$?\d+",
    r"click\s*here\s*now",
    r"(crypto|bitcoin|forex)\s*(profit|earn|signal)",
    r"(casino|gambling|bet)\s*\d+",
    r"(sell|buy)\s*(followers|views|likes)",
    r"https?://(?!t\.me|telegram\.me)[^\s]+\.(ru|cn|xyz|top|click)\b",
    r"\b(spam|flood|scam)\b",
    r"[А-Яа-я]{20,}",  # Too many Cyrillic chars (Spam in Russian)
]

SPAM_KEYWORDS = {
    "uz": ["pulga ishlang", "daromad", "sarmoya", "telegram orqali pul", "click qiling"],
    "en": ["earn money", "make profit", "free crypto", "click here", "investment opportunity"],
    "ru": ["заработок", "криптовалюта", "инвестиции", "кликай", "бесплатно"],
}


def is_spam_message(text: str, lang: str = "uz") -> tuple[bool, float]:
    """
    Check if message is spam.
    Returns (is_spam: bool, confidence: float 0-1)
    """
    if not text:
        return False, 0.0

    score = 0.0
    text_lower = text.lower()

    # Pattern matching
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            score += 0.3

    # Keyword check
    keywords = SPAM_KEYWORDS.get(lang, SPAM_KEYWORDS["en"])
    for kw in keywords:
        if kw in text_lower:
            score += 0.2

    # Heuristics
    if len(re.findall(r"http[s]?://", text)) >= 3:
        score += 0.4  # Multiple URLs

    if text.count("!!!") >= 3 or text.count("???") >= 3:
        score += 0.2  # Excessive punctuation

    if len([c for c in text if c.isupper()]) / max(len(text), 1) > 0.6:
        score += 0.2  # All caps

    score = min(score, 1.0)
    is_spam = score >= 0.5
    return is_spam, score


async def ai_spam_check(text: str) -> tuple[bool, str]:
    """Use AI to check if message is spam (more accurate but slower)."""
    try:
        from ai import ai_manager, Message
        response = await ai_manager.chat(
            messages=[
                Message(
                    role="system",
                    content=(
                        "You are a spam detector. Analyze the message and respond ONLY with:\n"
                        "SPAM or NOT_SPAM\n"
                        "followed by a brief reason (1 sentence)."
                    ),
                ),
                Message(role="user", content=f"Is this spam?\n\n{text[:500]}"),
            ]
        )
        result = response.text.strip().upper()
        is_spam = result.startswith("SPAM")
        reason = response.text.split("\n", 1)[-1].strip() if "\n" in response.text else ""
        return is_spam, reason
    except Exception:
        is_spam, _ = is_spam_message(text)
        return is_spam, "Pattern-based detection"
