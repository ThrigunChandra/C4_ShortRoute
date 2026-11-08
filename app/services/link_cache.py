import json

from redis.exceptions import RedisError

from app.database.redis_client import redis_client


def get_cached_link(key: str) -> dict | None:
    try:
        cached = redis_client.get(key)
    except RedisError:
        return None

    if cached is None:
        return None

    return json.loads(cached)


def cache_link(key: str, data: dict, ttl: int = 300) -> None:
    try:
        redis_client.set(
            key,
            json.dumps(data),
            ex=ttl
        )
    except RedisError:
        return

def delete_cached_links(*keys: str) -> None:
    if not keys:
        return

    try:
        redis_client.delete(*keys)
    except RedisError:
        return