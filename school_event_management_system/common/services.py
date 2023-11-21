from typing import Any

from config.redis import redis_connection


def is_cooldown_ended(key: str) -> bool:
    """Return True if cooldown has ended, False otherwise."""
    return not bool(redis_connection.get(key))


def set_key_with_timeout(key: str, timeout: int, value: int) -> Any:
    """Set a key-value pair in Redis with a specified timeout."""
    return redis_connection.setex(key, timeout, value)
