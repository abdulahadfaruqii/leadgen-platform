"""
Retry utilities with exponential backoff.
"""
import asyncio
import random
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")


def async_retry(max_retries: int = 3, backoff_base: float = 2.0, exceptions: tuple = (Exception,)):
    """Decorator for async retry with exponential backoff."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = backoff_base ** attempt + random.uniform(0, 1)
                    await asyncio.sleep(delay)
            return None
        return wrapper
    return decorator
