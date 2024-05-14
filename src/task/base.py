from typing import AsyncGenerator

import redis  # type: ignore
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, REDIS_HOST
from services.historic_candle import HistoricCandlesService
from services.security import SecuritiesService
from sqlalchemy import NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session = async_sessionmaker(engine)
redis_sync = redis.Redis.from_url(f"redis://{REDIS_HOST}:6379")

engine = create_engine(DATABASE_URL)
sync_session = sessionmaker(engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
        await session.commit()


async def _get_historic_candles_service_generator() -> AsyncGenerator[HistoricCandlesService, None]:
    async with async_session() as session:
        yield HistoricCandlesService(session)
        await session.commit()


async def _get_securities_service_generator() -> AsyncGenerator[SecuritiesService, None]:
    async with async_session() as session:
        yield SecuritiesService(session)
        await session.commit()


get_strategies_historic_candles_service = _get_historic_candles_service_generator()
get_strategies_securities_service = _get_securities_service_generator()
