"""
Hikmah AI — FastAPI Admin REST API
Provides HTTP endpoints for admin mini-app and webhook
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import settings
from database.sqlite import init_db, AsyncSessionLocal
from database.models import User, AIUsage, Movie, PromoCode
from utils.helpers import utc_now, format_number
from utils.logger import logger
from sqlalchemy import select, func, desc

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("✅ FastAPI started — Hikmah AI Admin API")
    yield
    logger.info("FastAPI stopped.")


app = FastAPI(
    title="Hikmah AI Admin API",
    description="Professional Telegram AI Platform — Admin REST API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Dashboard ─────────────────────────────────────────────

@app.get("/api/stats", tags=["Dashboard"])
async def get_stats(token: str = Depends(verify_token)):
    """Get overall statistics."""
    async with AsyncSessionLocal() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
        premium_users = (await session.execute(select(func.count(User.id)).where(User.is_premium == True))).scalar() or 0
        banned_users = (await session.execute(select(func.count(User.id)).where(User.is_banned == True))).scalar() or 0
        total_ai = (await session.execute(select(func.sum(User.total_requests)))).scalar() or 0
        total_points = (await session.execute(select(func.sum(User.points)))).scalar() or 0

    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "banned_users": banned_users,
        "total_ai_requests": total_ai,
        "total_points": total_points,
        "timestamp": utc_now().isoformat(),
    }


# ── Users ─────────────────────────────────────────────────

@app.get("/api/users", tags=["Users"])
async def get_users(
    page: int = 1,
    per_page: int = 50,
    premium_only: bool = False,
    token: str = Depends(verify_token),
):
    """Get paginated user list."""
    async with AsyncSessionLocal() as session:
        query = select(User)
        if premium_only:
            query = query.where(User.is_premium == True)
        query = query.order_by(desc(User.created_at)).offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(query)
        users = result.scalars().all()

    return {
        "page": page,
        "users": [
            {
                "id": u.telegram_id,
                "username": u.username,
                "full_name": u.full_name,
                "is_premium": u.is_premium,
                "premium_type": u.premium_type,
                "points": u.points,
                "total_requests": u.total_requests,
                "referral_count": u.referral_count,
                "is_banned": u.is_banned,
                "language": u.language,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_active": u.last_active.isoformat() if u.last_active else None,
            }
            for u in users
        ],
    }


@app.get("/api/users/{telegram_id}", tags=["Users"])
async def get_user(telegram_id: int, token: str = Depends(verify_token)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "full_name": user.full_name,
            "is_premium": user.is_premium,
            "premium_type": user.premium_type,
            "points": user.points,
            "level": user.level,
            "streak": user.streak,
            "total_requests": user.total_requests,
            "referral_code": user.referral_code,
            "referral_count": user.referral_count,
            "is_banned": user.is_banned,
        }


# ── Movies ────────────────────────────────────────────────

class MovieCreate(BaseModel):
    code: str
    title: str
    title_uz: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    is_islamic: bool = False


@app.get("/api/movies", tags=["Movies"])
async def get_movies(token: str = Depends(verify_token)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Movie).order_by(desc(Movie.created_at)).limit(100))
        movies = result.scalars().all()
    return {"movies": [{"id": m.id, "code": m.code, "title": m.title, "views": m.views, "is_active": m.is_active} for m in movies]}


@app.post("/api/movies", tags=["Movies"])
async def create_movie(data: MovieCreate, token: str = Depends(verify_token)):
    async with AsyncSessionLocal() as session:
        movie = Movie(**data.model_dump())
        session.add(movie)
        await session.commit()
        await session.refresh(movie)
    return {"id": movie.id, "code": movie.code, "message": "Movie created"}


# ── Promo Codes ───────────────────────────────────────────

class PromoCreate(BaseModel):
    premium_type: Optional[str] = None
    bonus_requests: int = 0
    bonus_points: int = 0
    max_uses: int = 1


@app.post("/api/promo", tags=["Promo"])
async def create_promo(data: PromoCreate, token: str = Depends(verify_token)):
    from utils.helpers import generate_promo_code
    code = generate_promo_code(10)
    async with AsyncSessionLocal() as session:
        promo = PromoCode(code=code, created_by=0, **data.model_dump())
        session.add(promo)
        await session.commit()
    return {"code": code, "message": "Promo code created"}


@app.get("/api/promo", tags=["Promo"])
async def list_promos(token: str = Depends(verify_token)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PromoCode).order_by(desc(PromoCode.created_at)).limit(50))
        promos = result.scalars().all()
    return {"promos": [{"code": p.code, "used": p.used_count, "max": p.max_uses, "type": p.premium_type} for p in promos]}


# ── Health ────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "Hikmah AI", "version": "2.0.0"}


@app.get("/", tags=["System"])
async def root():
    return {"message": "🤖 Hikmah AI Admin API", "docs": "/docs"}
