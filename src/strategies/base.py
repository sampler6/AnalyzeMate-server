from typing import AsyncGenerator

from config import TOKEN
from db.base import async_session
from services.historic_candle import HistoricCandlesService
from services.security import SecuritiesService
from tinkoff.invest import AsyncClient
from tinkoff.invest.async_services import AsyncServices


async def _get_async_tinkoff_api_client_generator() -> AsyncGenerator[AsyncServices, None]:
    if TOKEN is None:
        raise Exception("invalid tinkoff token")
    async with AsyncClient(TOKEN) as client:
        yield client


async def _get_historic_candles_service_generator() -> AsyncGenerator[HistoricCandlesService, None]:
    async with async_session() as session:
        yield HistoricCandlesService(session)


async def _get_securities_service_generator() -> AsyncGenerator[SecuritiesService, None]:
    async with async_session() as session:
        yield SecuritiesService(session)


get_tinkoff_client = _get_async_tinkoff_api_client_generator()
get_historic_candles_service = _get_historic_candles_service_generator()
get_securities_service = _get_securities_service_generator()
