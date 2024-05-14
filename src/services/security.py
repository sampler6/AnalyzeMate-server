import logging
from typing import Optional

from exceptions.base import ValidationException
from exceptions.securities import SecurityNotFoundError
from repositories.security import SecuritiesRepository
from securities.schemas import SecurityInSchema, SecurityOutSchema, SecurityShortOutSchema
from sqlalchemy.ext.asyncio import AsyncSession

from services.historic_candle import HistoricCandlesService

logger = logging.getLogger("api")


class SecuritiesService:
    def __init__(self, session: AsyncSession):
        self.repository = SecuritiesRepository(session)
        self.historic_candles_service = HistoricCandlesService(session)

    async def get_security_by_ticker(self, ticker: str) -> SecurityShortOutSchema:
        security = await self.repository.get_security_by_ticker(ticker)
        if not security:
            raise SecurityNotFoundError(ticker=ticker)

        return SecurityShortOutSchema(ticker=security.ticker, name=security.name, price=None)

    async def get_all_securities(self) -> list[SecurityShortOutSchema]:
        result = [
            SecurityShortOutSchema(
                ticker=security.ticker,
                name=security.name,
                price=security.price,
            )
            for security in await self.repository.get_all_securities()
        ]
        return result

    async def get_securities_by_tickers(
        self, tickers: list[str], include_historic_candles: bool, timeframe: Optional[int]
    ) -> list[SecurityOutSchema]:
        if include_historic_candles:
            if timeframe is None:
                raise ValidationException("Timeframe must be filled if include_historic_candles is True")
            result = [
                SecurityOutSchema(
                    ticker=security.ticker,
                    name=security.name,
                    price=security.price,
                    historic_candles=await self.historic_candles_service.get_historic_candles_by_ticker_and_timeframe(
                        security.ticker, timeframe
                    ),
                )
                for security in await self.repository.get_securities_by_tickers(tickers)
            ]
        else:
            result = [
                SecurityOutSchema(ticker=security.ticker, name=security.name, price=security.price)
                for security in await self.repository.get_securities_by_tickers(tickers)
            ]
        return result

    async def save_security(self, security: SecurityInSchema) -> None:
        await self.repository.save_security(security)

    async def save_securities(self, securities: list[SecurityInSchema]) -> None:
        await self.repository.save_securities(securities)

    async def search_security(self, search: str) -> list[SecurityShortOutSchema]:
        result_tickers = [ticker for ticker in await self.repository.search_security(search)]

        return [
            SecurityShortOutSchema(**x.model_dump())
            for x in await self.get_securities_by_tickers(result_tickers, False, None)
        ]
