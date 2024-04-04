from db.base import redis_db
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy

bearer_transport = BearerTransport(tokenUrl="auth/login/")


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis_db, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="redis",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)
