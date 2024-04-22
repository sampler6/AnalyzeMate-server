from asyncio import shield
from typing import AsyncGenerator

import redis.asyncio  # type: ignore
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, REDIS_HOST
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)

redis_db = redis.asyncio.from_url(f"redis://{REDIS_HOST}:6379", decode_responses=True)  # type: ignore


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await shield(session.close())


class Base(DeclarativeBase):
    __allow_unmapped__ = True
