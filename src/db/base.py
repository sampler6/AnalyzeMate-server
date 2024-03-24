import redis.asyncio  # type: ignore
from sqlalchemy.orm import DeclarativeBase

redis = redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)  # type: ignore


class Base(DeclarativeBase):
    pass
