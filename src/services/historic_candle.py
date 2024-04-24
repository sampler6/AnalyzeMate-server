from exceptions.securities import SecurityNotFoundError
from repositories.historic_candles import HistoricCandlesRepository
from repositories.security import SecuritiesRepository
from securities.schemas import HistoricCandlesOutSchema, HistoricCandlesSchema
from sqlalchemy.ext.asyncio import AsyncSession


class HistoricCandlesService:
    def __init__(self, session: AsyncSession):
        self.repository = HistoricCandlesRepository(session)
        self.securities_repository = SecuritiesRepository(session)

    async def get_historic_candles_by_ticker(self, ticker: str, timeframe: int) -> list[HistoricCandlesOutSchema]:
        if not await self.securities_repository.get_security_by_ticker(ticker):
            raise SecurityNotFoundError(ticker=ticker)

        result = await self.repository.get_historic_candles_by_ticker(ticker, timeframe)
        validated_result = []
        for historic_candle in result:
            validated_result.append(
                HistoricCandlesOutSchema(
                    open=historic_candle.open,
                    close=historic_candle.close,
                    volume=historic_candle.volume,
                    highest=historic_candle.highest,
                    lowest=historic_candle.lowest,
                    ticker=historic_candle.ticker,
                    timestamp=historic_candle.timestamp,
                    timeframe=historic_candle.timeframe,
                )
            )
        return validated_result

    async def save_historic_candle(self, historic_candle: HistoricCandlesSchema) -> None:
        await self.repository.save_historic_candle(historic_candle)

    async def save_historic_candles(self, historic_candles: list[HistoricCandlesSchema]) -> None:
        await self.repository.save_historic_candles(historic_candles)
