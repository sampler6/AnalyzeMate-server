from collections import defaultdict

from exceptions.securities import SecurityNotFoundError
from repositories.historic_candles import HistoricCandlesRepository
from repositories.security import SecuritiesRepository
from securities.schemas import HistoricCandlesOutSchema, HistoricCandlesSchema
from sqlalchemy.ext.asyncio import AsyncSession


class HistoricCandlesService:
    def __init__(self, session: AsyncSession):
        self.repository = HistoricCandlesRepository(session)
        self.securities_repository = SecuritiesRepository(session)

    async def get_historic_candles_by_ticker_and_timeframe(
        self, ticker: str, timeframe: int
    ) -> list[HistoricCandlesOutSchema]:
        if not await self.securities_repository.get_security_by_ticker(ticker):
            raise SecurityNotFoundError(ticker=ticker)

        result = await self.repository.get_historic_candles_by_ticker_and_timeframe(ticker, timeframe)
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

    async def get_existing_timestamp_for_all_tickers(self) -> dict[tuple[str, int], set[float]]:
        """
        Получение времен существующих свечей в бд в виде
        хэш-сета, с проверкой in(contains) за O(1)

        В ответ: словарь с ключом (ticker, timeframe) и значением хэш сет из timestamps
        """
        result = await self.repository.get_all_historic_candles()

        result_dict: dict[tuple[str, int], set[float]] = defaultdict(set)
        for candle in result:
            result_dict[(candle.ticker, candle.timeframe)].add(candle.timestamp)

        return result_dict

    async def insert_bulk(self, historic_candles: list[dict]) -> None:
        """Запись большого числа свечей с помощью insert bulk mode sqlalchemy"""
        await self.repository.insert_bulk(historic_candles)
