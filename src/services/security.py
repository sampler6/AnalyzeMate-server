import logging

from exceptions.securities import SecurityNotFoundError
from repositories.security import SecuritiesRepository
from securities.schemas import SecurityInSchema, SecurityOutSchema
from sqlalchemy.ext.asyncio import AsyncSession

from services.historic_candle import HistoricCandlesService

logger = logging.getLogger("api")


class SecuritiesService:
    def __init__(self, session: AsyncSession):
        self.repository = SecuritiesRepository(session)
        self.historic_candles_service = HistoricCandlesService(session)

    async def get_security_by_ticker(self, ticker: str) -> SecurityOutSchema:
        security = await self.repository.get_security_by_ticker(ticker)
        if not security:
            raise SecurityNotFoundError(ticker=ticker)

        return SecurityOutSchema(ticker=security.ticker, name=security.name)

    async def get_all_securities(self) -> list[SecurityOutSchema]:
        result = [
            SecurityOutSchema(ticker=security.ticker, name=security.name)
            for security in await self.repository.get_all_securities()
        ]
        return result

    async def get_securities_by_tickers(
        self, tickers: list[str], include_historic_candles: bool
    ) -> list[SecurityOutSchema]:
        if include_historic_candles:
            result = [
                SecurityOutSchema(
                    ticker=security.ticker,
                    name=security.name,
                    historic_candles=await self.historic_candles_service.get_historic_candles_by_ticker(
                        security.ticker
                    ),
                )
                for security in await self.repository.get_securities_by_tickers(tickers)
            ]
        else:
            result = [
                SecurityOutSchema(ticker=security.ticker, name=security.name)
                for security in await self.repository.get_securities_by_tickers(tickers)
            ]
        return result

    async def save_security(self, security: SecurityInSchema) -> None:
        await self.repository.save_security(security)

    async def save_securities(self, securities: list[SecurityInSchema]) -> None:
        await self.repository.save_securities(securities)
