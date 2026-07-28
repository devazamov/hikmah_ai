"""
Hikmah AI — Channel/Subscription Service
"""
from __future__ import annotations

from typing import List, Optional

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from config.settings import settings
from utils.logger import logger


class ChannelService:

    @staticmethod
    async def check_subscription(bot: Bot, user_id: int) -> tuple[bool, List[int]]:
        """
        Check if user is subscribed to all required channels.
        Returns (all_subscribed: bool, unsubscribed_channels: List[int])
        """
        if not settings.subscription_check_enabled:
            return True, []

        channels = settings.required_channels_list
        if not channels:
            return True, []

        unsubscribed = []
        for channel_id in channels:
            try:
                member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                if member.status in (
                    ChatMemberStatus.LEFT,
                    ChatMemberStatus.KICKED,
                    ChatMemberStatus.BANNED,
                ):
                    unsubscribed.append(channel_id)
            except Exception as e:
                logger.warning(f"Could not check subscription for channel {channel_id}: {e}")

        return len(unsubscribed) == 0, unsubscribed

    @staticmethod
    async def get_channel_invite_links(bot: Bot, channel_ids: List[int]) -> List[dict]:
        """Get channel info and invite links."""
        channels = []
        for channel_id in channel_ids:
            try:
                chat = await bot.get_chat(channel_id)
                invite_link = getattr(chat, "invite_link", None)
                if not invite_link:
                    try:
                        link_obj = await bot.create_chat_invite_link(channel_id)
                        invite_link = link_obj.invite_link
                    except Exception:
                        invite_link = None
                channels.append({
                    "id": channel_id,
                    "title": chat.title or str(channel_id),
                    "username": getattr(chat, "username", None),
                    "invite_link": invite_link,
                })
            except Exception as e:
                logger.warning(f"Cannot get channel {channel_id} info: {e}")
                channels.append({
                    "id": channel_id,
                    "title": str(channel_id),
                    "username": None,
                    "invite_link": None,
                })
        return channels
