"""
Hikmah AI — Decorators
"""
from __future__ import annotations

import asyncio
import functools
from typing import Callable, TypeVar

from utils.logger import logger

F = TypeVar("F", bound=Callable)


def log_handler(func: F) -> F:
    """Log entry/exit of every handler."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.debug(f"Handler called: {func.__name__}")
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Handler {func.__name__} raised: {e}")
            raise
    return wrapper  # type: ignore


def retry(times: int = 3, delay: float = 1.0):
    """Retry an async function on failure."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == times:
                        raise
                    logger.warning(f"Retry {attempt}/{times} for {func.__name__}: {e}")
                    await asyncio.sleep(delay * attempt)
        return wrapper  # type: ignore
    return decorator
