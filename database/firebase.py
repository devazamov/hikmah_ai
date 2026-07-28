"""
Hikmah AI — Firebase Firestore Client
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from utils.logger import logger

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore_v1.async_client import AsyncClient
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("firebase-admin not installed; Firebase features disabled.")

from config.settings import settings

_db: Optional[Any] = None


def init_firebase() -> bool:
    """Initialize Firebase Admin SDK. Returns True if successful."""
    global _db

    if not FIREBASE_AVAILABLE:
        return False

    if not settings.firebase_enabled:
        logger.warning("Firebase credentials not set in .env — Firebase disabled.")
        return False

    try:
        if not firebase_admin._apps:
            cred_dict = {
                "type": "service_account",
                "project_id": settings.firebase_project_id,
                "private_key_id": settings.firebase_private_key_id,
                "private_key": (settings.firebase_private_key or "").replace("\\n", "\n"),
                "client_email": settings.firebase_client_email,
                "client_id": settings.firebase_client_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)

        _db = firestore.client()
        logger.info(f"✅ Firebase connected: {settings.firebase_project_id}")
        return True
    except Exception as e:
        logger.error(f"Firebase init failed: {e}")
        return False


def get_db():
    return _db


# ── Firestore Collection Helpers ─────────────────────────

COLLECTIONS = {
    "users": "users",
    "admins": "admins",
    "statistics": "statistics",
    "settings": "settings",
    "feedback": "feedback",
    "broadcasts": "broadcasts",
    "channels": "channels",
    "logs": "logs",
    "referrals": "referrals",
    "ai_usage": "ai_usage",
    "premium": "premium",
    "movies": "movies",
    "support": "support_tickets",
}


async def fb_set(collection: str, doc_id: str, data: Dict[str, Any], merge: bool = True) -> bool:
    if _db is None:
        return False
    try:
        ref = _db.collection(collection).document(str(doc_id))
        ref.set(data, merge=merge)
        return True
    except Exception as e:
        logger.error(f"Firebase set error [{collection}/{doc_id}]: {e}")
        return False


async def fb_get(collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
    if _db is None:
        return None
    try:
        ref = _db.collection(collection).document(str(doc_id))
        doc = ref.get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        logger.error(f"Firebase get error [{collection}/{doc_id}]: {e}")
        return None


async def fb_update(collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
    if _db is None:
        return False
    try:
        ref = _db.collection(collection).document(str(doc_id))
        ref.update(data)
        return True
    except Exception as e:
        logger.error(f"Firebase update error [{collection}/{doc_id}]: {e}")
        return False


async def fb_delete(collection: str, doc_id: str) -> bool:
    if _db is None:
        return False
    try:
        _db.collection(collection).document(str(doc_id)).delete()
        return True
    except Exception as e:
        logger.error(f"Firebase delete error [{collection}/{doc_id}]: {e}")
        return False


async def fb_query(
    collection: str,
    filters: Optional[List] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    if _db is None:
        return []
    try:
        ref = _db.collection(collection)
        if filters:
            for f in filters:
                ref = ref.where(*f)
        docs = ref.limit(limit).get()
        return [d.to_dict() for d in docs if d.exists]
    except Exception as e:
        logger.error(f"Firebase query error [{collection}]: {e}")
        return []


async def fb_increment(collection: str, doc_id: str, field: str, amount: int = 1) -> bool:
    if _db is None:
        return False
    try:
        from google.cloud.firestore_v1 import transforms
        ref = _db.collection(collection).document(str(doc_id))
        ref.update({field: transforms.SERVER_TIMESTAMP if amount == 0 else firestore.Increment(amount)})
        return True
    except Exception as e:
        logger.error(f"Firebase increment error: {e}")
        return False
