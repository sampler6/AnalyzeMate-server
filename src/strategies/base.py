from typing import AsyncGenerator

from config import TOKEN
from db.base import async_session
from repositories.historic_candles import HistoricCandlesRepository
from repositories.security import SecuritiesRepository
from tinkoff.invest import AsyncClient
from tinkoff.invest.async_services import AsyncServices


async def _get_async_tinkoff_api_client_generator() -> AsyncGenerator[AsyncServices, None]:
    if TOKEN is None:
        raise Exception("invalid tinkoff token")
    async with AsyncClient(TOKEN) as client:
        yield client


async def _get_historic_candle_repository_generator() -> AsyncGenerator[HistoricCandlesRepository, None]:
    async with async_session() as session:
        yield HistoricCandlesRepository(session)


async def _get_securities_repository_generator() -> AsyncGenerator[SecuritiesRepository, None]:
    async with async_session() as session:
        yield SecuritiesRepository(session)


get_tinkoff_client = _get_async_tinkoff_api_client_generator()
