"""
Hikmah AI — User Repository
Data access layer for User model
"""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy import select, update, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from utils.helpers import utc_now


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_referral_code(self, code: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.referral_code == code))
        return result.scalar_one_or_none()

    async def get_all_active(self, limit: int = 5000) -> List[User]:
        result = await self.session.execute(
            select(User).where(User.is_active == True, User.is_banned == False).limit(limit)
        )
        return list(result.scalars().all())

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar() or 0

    async def count_premium(self) -> int:
        result = await self.session.execute(select(func.count(User.id)).where(User.is_premium == True))
        return result.scalar() or 0

    async def count_active_today(self) -> int:
        from datetime import datetime, timezone
        today = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0)
        result = await self.session.execute(
            select(func.count(User.id)).where(User.last_active >= today)
        )
        return result.scalar() or 0

    async def get_top_by_points(self, limit: int = 10) -> List[User]:
        result = await self.session.execute(
            select(User).order_by(desc(User.points)).limit(limit)
        )
        return list(result.scalars().all())

    async def get_top_referrers(self, limit: int = 10) -> List[User]:
        result = await self.session.execute(
            select(User).order_by(desc(User.referral_count)).limit(limit)
        )
        return list(result.scalars().all())

    async def update_last_active(self, telegram_id: int) -> None:
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(last_active=utc_now())
        )
        await self.session.commit()

    async def search(self, query: str) -> List[User]:
        result = await self.session.execute(
            select(User).where(
                User.username.ilike(f"%{query}%") |
                User.full_name.ilike(f"%{query}%")
            ).limit(20)
        )
        return list(result.scalars().all())
