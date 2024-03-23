from typing import Any

from config.redis import redis_connection


def is_cooldown_ended(key: str) -> bool:
    """Возвращает True, если время восстановления закончилось, в противном случае — False."""
    return not bool(redis_connection.get(key))


def set_key_with_timeout(key: str, timeout: int, value: int) -> Any:
    """Установите пару ключ-значение в Redis с указанным таймаутом."""
    return redis_connection.setex(key, timeout, value)
