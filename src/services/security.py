import logging

from exceptions.base import ResourceNotFoundException
from repositories.security import SecuritiesRepository
from securities.schemas import SecurityOutSchema
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("api")


class SecurityService:
    def __init__(self, session: AsyncSession):
        self.repository = SecuritiesRepository(session)

    async def get_security_by_ticker(self, ticker: str) -> SecurityOutSchema:
        security = await self.repository.get_security_by_ticker(ticker)
        if not security:
            raise ResourceNotFoundException(template="Security not found: ticker={ticker}", ticker=ticker)

        return SecurityOutSchema(ticker=security.ticker, name=security.name)

    async def get_all_securities(self) -> list[SecurityOutSchema]:
        return [
            SecurityOutSchema(ticker=security.ticker, name=security.name)
            for security in await self.repository.get_all_securities()
        ]

    async def get_securities_by_tickers(self, tickers: list[str]) -> list[SecurityOutSchema]:
        return [
            SecurityOutSchema(ticker=security.ticker, name=security.name)
            for security in await self.repository.get_securities_by_tickers(tickers)
        ]
