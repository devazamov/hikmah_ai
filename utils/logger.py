"""
Hikmah AI — Centralized Logger
Uses loguru for structured, colorful, async-safe logging
"""
import sys
from loguru import logger
from config.settings import settings


def setup_logger() -> None:
    logger.remove()

    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
        "<level>{message}</level>"
    )

    logger.add(sys.stdout, format=fmt, level=settings.log_level, colorize=True)
    logger.add(
        "logs/hikmah_ai.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        level="DEBUG",
        encoding="utf-8",
        format=fmt,
    )
    logger.add(
        "logs/errors.log",
        rotation="5 MB",
        retention="60 days",
        compression="zip",
        level="ERROR",
        encoding="utf-8",
        format=fmt,
    )


setup_logger()
__all__ = ["logger"]
