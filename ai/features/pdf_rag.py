"""
Hikmah AI — PDF Chat (RAG — Retrieval Augmented Generation)
Upload PDF → Ask questions about it
"""
from __future__ import annotations

import io
import asyncio
import os
import tempfile
from typing import Optional

from ai import ai_manager, Message
from ai.base import AIResponse
from utils.logger import logger


async def extract_pdf_text(pdf_data: bytes) -> Optional[str]:
    """Extract text from PDF bytes."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_data))
        texts = []
        for page in reader.pages[:20]:  # Max 20 pages
            text = page.extract_text()
            if text:
                texts.append(text.strip())
        return "\n\n".join(texts)
    except ImportError:
        logger.error("pypdf not installed. Run: pip install pypdf")
        return None
    except Exception as e:
        logger.error(f"PDF extract error: {e}")
        return None


# In-memory PDF storage per user (user_id -> text)
_pdf_contexts: dict[int, str] = {}


def store_pdf_context(user_id: int, text: str) -> None:
    _pdf_contexts[user_id] = text[:15000]  # 15K char limit


def get_pdf_context(user_id: int) -> Optional[str]:
    return _pdf_contexts.get(user_id)


def clear_pdf_context(user_id: int) -> None:
    _pdf_contexts.pop(user_id, None)


async def chat_with_pdf(user_id: int, question: str) -> AIResponse:
    """Answer question based on stored PDF context."""
    context = get_pdf_context(user_id)
    if not context:
        return AIResponse(
            text="❌ PDF hali yuklanmagan. Avval PDF fayl yuboring.",
            provider="local",
            model="rag",
            success=False,
        )

    prompt = (
        f"Quyidagi hujjat matni asosida savolga javob ber. "
        f"Faqat hujjatdagi ma'lumotlardan foydalanish. "
        f"Agar javob hujjatda yo'q bo'lsa, shunday de.\n\n"
        f"HUJJAT:\n{context[:8000]}\n\n"
        f"SAVOL: {question}"
    )

    messages = [
        Message(role="system", content="Sen PDF hujjatlar bo'yicha savol-javob mutaxassisisan."),
        Message(role="user", content=prompt),
    ]
    return await ai_manager.chat(messages=messages)
