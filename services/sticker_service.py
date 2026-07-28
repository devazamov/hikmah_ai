"""
Hikmah AI — Sticker Maker Service
Creates Telegram-compatible WebP stickers from images/text
"""
from __future__ import annotations

import io
from typing import Optional, Tuple


async def create_text_sticker(
    text: str,
    emoji: str = "😊",
    bg_color: str = "#1a1a2e",
    text_color: str = "#e0e0ff",
) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Create a sticker from text.
    Returns (webp_bytes, error_message)
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap

        W, H = 512, 512
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background circle
        margin = 20
        draw.ellipse([margin, margin, W - margin, H - margin], fill=bg_color)

        # Wrap text
        wrapped = textwrap.fill(text, width=12)

        # Font
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48
            )
        except Exception:
            font = ImageFont.load_default()

        # Center text
        bbox = draw.textbbox((0, 0), wrapped, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(((W - tw) / 2, (H - th) / 2 - 30), wrapped, fill=text_color, font=font)

        # Emoji at bottom
        try:
            emoji_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 72
            )
            draw.text((W // 2 - 36, H - 130), emoji, font=emoji_font, embedded_color=True)
        except Exception:
            pass

        buf = io.BytesIO()
        img.save(buf, format="WEBP")
        buf.seek(0)
        return buf.read(), None

    except ImportError:
        return None, "❌ Sticker yaratish uchun Pillow o'rnatilmagan: pip install pillow"
    except Exception as e:
        return None, f"❌ Sticker xatosi: {str(e)[:100]}"


async def image_to_sticker(image_bytes: bytes) -> Tuple[Optional[bytes], Optional[str]]:
    """Convert any image to sticker-compatible WebP (512x512)."""
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        img = img.resize((512, 512), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="WEBP")
        buf.seek(0)
        return buf.read(), None
    except ImportError:
        return None, "❌ Pillow o'rnatilmagan. pip install pillow"
    except Exception as e:
        return None, f"❌ Xatolik: {str(e)[:100]}"
