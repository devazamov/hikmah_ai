"""
Hikmah AI — Referral Service (Full Implementation)
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from config.settings import settings
from utils.helpers import generate_referral_code
from utils.logger import logger


class ReferralService:

    @staticmethod
    def generate_link(bot_username: str, referral_code: str) -> str:
        return f"https://t.me/{bot_username}?start=ref_{referral_code}"

    @staticmethod
    async def process_referral(
        session: AsyncSession,
        new_user_id: int,
        ref_code: str,
    ) -> bool:
        """
        Process referral when new user joins.
        Returns True if referral was valid and processed.
        """
        result = await session.execute(
            select(User).where(User.referral_code == ref_code)
        )
        referrer = result.scalar_one_or_none()

        if not referrer or referrer.telegram_id == new_user_id:
            return False

        # Give bonus to referrer
        referrer.bonus_requests += settings.referral_bonus_requests
        referrer.referral_count += 1
        referrer.points += 50  # 50 points per successful referral

        await session.commit()
        logger.info(f"Referral processed: {new_user_id} referred by {referrer.telegram_id}")
        return True

    @staticmethod
    async def get_referral_stats(session: AsyncSession, user_id: int) -> dict:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {}

        return {
            "referral_code": user.referral_code,
            "referral_count": user.referral_count,
            "bonus_requests": user.bonus_requests,
            "link": ReferralService.generate_link(settings.bot_username, user.referral_code or ""),
            "points_earned": user.referral_count * 50,
        }

    @staticmethod
    async def get_top_referrers(session: AsyncSession, limit: int = 10) -> list[User]:
        from sqlalchemy import desc
        result = await session.execute(
            select(User).order_by(desc(User.referral_count)).limit(limit)
        )
        return list(result.scalars().all())
