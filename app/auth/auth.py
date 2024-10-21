from fastapi_users.authentication import CookieTransport
import redis.asyncio
from fastapi_users.authentication import RedisStrategy
from fastapi_users.authentication import AuthenticationBackend


cookie_transport = CookieTransport(
    cookie_name='instant_messages_cookie',
    cookie_max_age=3600,
)

redis = redis.asyncio.from_url(
    "redis://cache:6379",
    decode_responses=True
)

def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="redis",
    transport=cookie_transport,
    get_strategy=get_redis_strategy,
)