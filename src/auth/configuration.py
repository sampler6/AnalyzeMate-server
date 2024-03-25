from db.base import redis
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy

bearer_transport = BearerTransport(tokenUrl="auth/token1/")


def get_redis_strategy() -> RedisStrategy:  # type: ignore
    return RedisStrategy(redis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="redis",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)
