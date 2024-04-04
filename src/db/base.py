from typing import AsyncGenerator

import redis.asyncio  # type: ignore
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, REDIS_HOST
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

redis_db = redis.asyncio.from_url(f"redis://{REDIS_HOST}:6379", decode_responses=True)  # type: ignore


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
        await session.commit()


class Base(DeclarativeBase):
    pass
