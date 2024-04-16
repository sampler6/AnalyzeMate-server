from db.base import get_async_session
from fastapi import Depends
from services.historic_candle import HistoricCandlesService
from services.portfolio import PortfolioService
from services.security import SecuritiesService
from sqlalchemy.ext.asyncio import AsyncSession


async def get_security_service(session: AsyncSession = Depends(get_async_session)) -> SecuritiesService:
    return SecuritiesService(session=session)


async def get_portfolio_service(session: AsyncSession = Depends(get_async_session)) -> PortfolioService:
    return PortfolioService(session=session)


async def get_historic_candles_service(session: AsyncSession = Depends(get_async_session)) -> HistoricCandlesService:
    return HistoricCandlesService(session)
