"""
Hikmah AI — Video Download Service (yt-dlp)
Supports: YouTube, Instagram, TikTok, Facebook, Twitter, VK and 1000+ sites
"""
from __future__ import annotations

import asyncio
import os
import tempfile
from typing import Optional, Tuple

from utils.logger import logger

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False


async def download_video(
    url: str,
    quality: str = "best[height<=720]",
    audio_only: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Download video from URL.
    Returns (file_path, error_message).
    file_path is None on error.
    """
    if not YTDLP_AVAILABLE:
        return None, "yt-dlp o'rnatilmagan. `pip install yt-dlp` bajaring."

    tmp_dir = tempfile.mkdtemp()
    output_template = os.path.join(tmp_dir, "%(title)s.%(ext)s")

    format_str = "bestaudio/best" if audio_only else f"{quality}/best[height<=720]/best"

    ydl_opts = {
        "format": format_str,
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": 50 * 1024 * 1024,  # 50 MB limit for Telegram
        "retries": 3,
        "socket_timeout": 30,
    }

    if audio_only:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: _download_sync(url, ydl_opts, tmp_dir))
        return result
    except Exception as e:
        logger.error(f"Video download error: {e}")
        return None, f"Yuklab olishda xatolik: {str(e)[:150]}"


def _download_sync(url: str, opts: dict, tmp_dir: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None, "Video ma'lumotlari topilmadi."

            # Find downloaded file
            for f in os.listdir(tmp_dir):
                filepath = os.path.join(tmp_dir, f)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    if size > 50 * 1024 * 1024:
                        os.remove(filepath)
                        return None, "❌ Fayl hajmi 50 MB dan katta (Telegram limiti)."
                    return filepath, None

        return None, "Fayl yuklab olinmadi."
    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if "Private" in msg or "private" in msg:
            return None, "❌ Bu video yopiq (private)."
        if "age" in msg.lower():
            return None, "❌ Bu video yosh chekloviga ega."
        return None, f"❌ Yuklab olish xatosi: {msg[:100]}"
    except Exception as e:
        return None, f"❌ Xatolik: {str(e)[:100]}"


async def get_video_info(url: str) -> Optional[dict]:
    """Get video info without downloading."""
    if not YTDLP_AVAILABLE:
        return None

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: _get_info_sync(url, ydl_opts)
        )
        return info
    except Exception as e:
        logger.error(f"Video info error: {e}")
        return None


def _get_info_sync(url: str, opts: dict) -> Optional[dict]:
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None
            return {
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "view_count": info.get("view_count", 0),
                "thumbnail": info.get("thumbnail"),
                "webpage_url": info.get("webpage_url", url),
            }
    except Exception:
        return None
