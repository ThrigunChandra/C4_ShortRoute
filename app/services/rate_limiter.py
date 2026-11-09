import math
from app.database.redis_client import redis_client

def check_rate_limit(
    key: str,
    limit: int,
    window: int = 60,
) -> tuple[bool, int]:
    # Run the counter and expiry operations together
    with redis_client.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key, window, nx=True)
        pipe.pttl(key)

        count, _, remaining_ms = pipe.execute()

    limited = count > limit
    retry_after = max(1, math.ceil(remaining_ms / 1000))

    return limited, retry_after