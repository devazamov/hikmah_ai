"""
Hikmah AI — Text Formatters & HTML Helpers
"""
from __future__ import annotations
import re
from datetime import datetime, timezone


def escape_html(text: str) -> str:
    """Escape Telegram HTML special chars."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def bold(text: str) -> str:
    return f"<b>{text}</b>"


def italic(text: str) -> str:
    return f"<i>{text}</i>"


def code(text: str) -> str:
    return f"<code>{text}</code>"


def link(text: str, url: str) -> str:
    return f'<a href="{url}">{text}</a>'


def spoiler(text: str) -> str:
    return f"<tg-spoiler>{text}</tg-spoiler>"


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 ** 2:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 ** 3:
        return f"{bytes_size / 1024 ** 2:.1f} MB"
    return f"{bytes_size / 1024 ** 3:.1f} GB"


def format_duration(seconds: int) -> str:
    """Format seconds to mm:ss or hh:mm:ss."""
    if seconds < 3600:
        return f"{seconds // 60:02d}:{seconds % 60:02d}"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_datetime_uz(dt: datetime) -> str:
    """Format datetime in Uzbek-friendly format."""
    months = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return f"{dt.day} {months[dt.month - 1]} {dt.year}, {dt.hour:02d}:{dt.minute:02d}"


def clean_ai_response(text: str) -> str:
    """Clean AI response for Telegram HTML display."""
    # Remove markdown bold/italic (convert to HTML)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Remove excessive newlines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text.strip()


def split_long_message(text: str, max_len: int = 4000) -> list[str]:
    """Split long text into Telegram-safe chunks."""
    if len(text) <= max_len:
        return [text]
    parts = []
    while text:
        if len(text) <= max_len:
            parts.append(text)
            break
        # Try to split at newline
        split_at = text.rfind('\n', 0, max_len)
        if split_at == -1:
            split_at = max_len
        parts.append(text[:split_at])
        text = text[split_at:].lstrip('\n')
    return parts
