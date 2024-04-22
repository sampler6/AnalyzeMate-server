from typing import AsyncGenerator

from db.base import DATABASE_URL
from services.historic_candle import HistoricCandlesService
from services.security import SecuritiesService
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
        await session.commit()


async def _get_historic_candles_service_generator() -> AsyncGenerator[HistoricCandlesService, None]:
    async with async_session() as session:
        yield HistoricCandlesService(session)


async def _get_securities_service_generator() -> AsyncGenerator[SecuritiesService, None]:
    async with async_session() as session:
        yield SecuritiesService(session)


get_strategies_historic_candles_service = _get_historic_candles_service_generator()
get_strategies_securities_service = _get_securities_service_generator()
