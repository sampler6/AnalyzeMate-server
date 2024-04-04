from typing import Any, AsyncGenerator, Iterable, Optional

import redis.asyncio  # type: ignore
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, REDIS_HOST
from sqlalchemy import Delete, Insert, Result, Select, Update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

redis = redis.asyncio.from_url(f"redis://{REDIS_HOST}:6379", decode_responses=True)  # type: ignore


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


class Base(DeclarativeBase):
    pass


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, statement: Select[Any] | Delete[Any] | Update[Any] | Insert[Any]) -> Result:
        return await self.session.execute(statement)

    async def all(self, statement: Select[Any] | Delete[Any] | Update[Any] | Insert[Any]) -> Iterable[Any]:
        return (await self.execute(statement)).all()

    async def one_or_none(self, statement: Select[Any] | Delete[Any] | Update[Any] | Insert[Any]) -> Optional[Any]:
        return (await self.execute(statement)).one_or_none()
