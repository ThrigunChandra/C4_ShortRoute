from redis import Redis

from app.config import REDIS_URL

redis_client = Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1
)