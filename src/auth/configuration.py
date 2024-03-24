import redis.asyncio  # type: ignore
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy

bearer_transport = BearerTransport(tokenUrl="auth/token/")


redis = redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)


def get_redis_strategy() -> RedisStrategy:  # type: ignore
    return RedisStrategy(redis, lifetime_seconds=3600)  # type: ignore


auth_backend = AuthenticationBackend(
    name="redis",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)
