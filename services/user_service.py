"""
Hikmah AI — User Service
Handles user registration, limits, gamification
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Achievement
from database.firebase import fb_set, fb_get
from config.settings import settings
from utils.helpers import generate_referral_code, utc_now, level_info, progress_bar
from utils.logger import logger


class UserService:

    @staticmethod
    async def get_or_create(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        full_name: str = "",
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        referred_by: Optional[int] = None,
    ) -> tuple[User, bool]:
        """Get existing user or create new. Returns (user, is_new)."""
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

        if user:
            # Update last active + basic info
            user.last_active = utc_now()
            if username:
                user.username = username
            user.full_name = full_name
            await session.commit()
            return user, False

        # Create new user
        ref_code = generate_referral_code(telegram_id)
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            referral_code=ref_code,
            referred_by=referred_by,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Sync to Firebase
        await fb_set("users", str(telegram_id), {
            "telegram_id": telegram_id,
            "username": username,
            "full_name": full_name,
            "referral_code": ref_code,
            "is_premium": False,
            "created_at": utc_now().isoformat(),
        })

        # Handle referral bonus
        if referred_by:
            await UserService.add_referral_bonus(session, referred_by, settings.referral_bonus_requests)

        logger.info(f"New user: {telegram_id} @{username}")
        return user, True

    @staticmethod
    async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def check_limit(session: AsyncSession, user: User) -> tuple[bool, int, int]:
        """
        Check if user can make AI request.
        Returns (can_use: bool, used: int, total: int)
        """
        today = utc_now().strftime("%Y-%m-%d")

        # Reset daily counter if new day
        if user.daily_reset_date != today:
            user.daily_requests_used = 0
            user.daily_reset_date = today
            await session.commit()

        # Determine limit
        if user.is_premium:
            if user.premium_type == "ultra":
                return True, user.daily_requests_used, 999999
            total = settings.premium_daily_limit if user.premium_type == "premium" else settings.pro_daily_limit
        else:
            total = settings.free_daily_limit

        # Add bonus requests
        effective_total = total + user.bonus_requests
        used = user.daily_requests_used

        return used < effective_total, used, effective_total

    @staticmethod
    async def increment_usage(session: AsyncSession, user: User) -> None:
        """Increment daily usage counter and total stats."""
        user.daily_requests_used += 1
        user.total_requests += 1
        user.points += 2  # 2 points per AI request
        user.last_active = utc_now()

        # Level up check
        info = level_info(user.points)
        new_level = list(info.keys()).index("min") if "min" in info else 1
        # simpler level calc
        if user.points >= 10000:
            user.level = 6
        elif user.points >= 4000:
            user.level = 5
        elif user.points >= 1500:
            user.level = 4
        elif user.points >= 500:
            user.level = 3
        elif user.points >= 100:
            user.level = 2
        else:
            user.level = 1

        await session.commit()

    @staticmethod
    async def add_referral_bonus(session: AsyncSession, referrer_id: int, bonus: int) -> None:
        result = await session.execute(select(User).where(User.telegram_id == referrer_id))
        referrer = result.scalar_one_or_none()
        if referrer:
            referrer.bonus_requests += bonus
            referrer.referral_count += 1
            referrer.points += 50  # 50 points for referral
            await session.commit()
            logger.info(f"Referral bonus +{bonus} to {referrer_id}")

    @staticmethod
    async def claim_daily_bonus(session: AsyncSession, user: User) -> tuple[bool, int, int]:
        """
        Claim daily bonus. Returns (claimed: bool, bonus_points: int, streak: int).
        """
        today = utc_now().strftime("%Y-%m-%d")
        if user.last_daily_bonus == today:
            return False, 0, user.streak

        # Calculate streak
        from datetime import timedelta
        yesterday = (utc_now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if user.last_daily_bonus == yesterday:
            user.streak += 1
        else:
            user.streak = 1

        # Bonus based on streak
        base_bonus = 10
        streak_bonus = min(user.streak * 5, 100)
        total_bonus = base_bonus + streak_bonus

        user.points += total_bonus
        user.last_daily_bonus = today
        await session.commit()

        # Check streak achievements
        await UserService.check_achievements(session, user)

        return True, total_bonus, user.streak

    @staticmethod
    async def check_achievements(session: AsyncSession, user: User) -> list[str]:
        """Check and award achievements. Returns list of new badge keys."""
        new_badges = []

        badges = {
            "first_message": user.total_requests >= 1,
            "power_user": user.total_requests >= 100,
            "ai_master": user.total_requests >= 1000,
            "streak_7": user.streak >= 7,
            "streak_30": user.streak >= 30,
            "referral_5": user.referral_count >= 5,
            "referral_10": user.referral_count >= 10,
            "level_3": user.level >= 3,
            "level_5": user.level >= 5,
        }

        for badge, condition in badges.items():
            if not condition:
                continue
            # Check if already has badge
            existing = await session.execute(
                select(Achievement).where(
                    Achievement.telegram_id == user.telegram_id,
                    Achievement.badge == badge
                )
            )
            if not existing.scalar_one_or_none():
                session.add(Achievement(telegram_id=user.telegram_id, badge=badge))
                new_badges.append(badge)

        if new_badges:
            await session.commit()
        return new_badges

    @staticmethod
    async def set_premium(
        session: AsyncSession,
        user: User,
        premium_type: str,
        days: int,
    ) -> None:
        from datetime import timedelta
        user.is_premium = True
        user.premium_type = premium_type
        user.premium_expires = utc_now() + timedelta(days=days)
        await session.commit()
        await fb_set("premium", str(user.telegram_id), {
            "telegram_id": user.telegram_id,
            "type": premium_type,
            "expires": user.premium_expires.isoformat(),
        })

    @staticmethod
    async def remove_premium(session: AsyncSession, user: User) -> None:
        user.is_premium = False
        user.premium_type = None
        user.premium_expires = None
        await session.commit()

    @staticmethod
    async def ban(session: AsyncSession, user: User) -> None:
        user.is_banned = True
        user.is_active = False
        await session.commit()

    @staticmethod
    async def unban(session: AsyncSession, user: User) -> None:
        user.is_banned = False
        user.is_active = True
        await session.commit()
