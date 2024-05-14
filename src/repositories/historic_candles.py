import logging
from typing import Iterable

from db.base_repository import BaseRepository
from securities.models import HistoricCandles
from securities.schemas import HistoricCandlesSchema
from sqlalchemy import and_, desc, insert, select

logger = logging.getLogger("api")


class HistoricCandlesRepository(BaseRepository):
    async def get_historic_candles_by_ticker_and_timeframe(
        self, ticker: str, timeframe: int
    ) -> Iterable[HistoricCandles]:
        statement = (
            select(HistoricCandles)
            .where(and_(HistoricCandles.ticker == ticker, HistoricCandles.timeframe == timeframe))
            .order_by(desc(HistoricCandles.timestamp))
        )
        return await self.all(statement)

    async def save_historic_candle(self, historic_candle: HistoricCandlesSchema) -> None:
        model = historic_candle.model_dump()
        model["timeframe"] = model["timeframe"].value
        historic_candle_db = HistoricCandles(**historic_candle.model_dump())

        await self.save(historic_candle_db)
        await self.session.commit()

    async def save_historic_candles(self, historic_candles: list[HistoricCandlesSchema]) -> None:
        historic_candles_db: list[HistoricCandles] = list()
        for historic_candle in historic_candles:
            historic_candles_db.append(HistoricCandles(**historic_candle.model_dump()))

        await self.save_all(historic_candles_db)
        await self.session.commit()

    async def insert_bulk(self, historic_candles: list[dict]) -> None:
        """Запись большого числа свечей с помощью insert bulk mode sqlalchemy"""
        stmt = insert(HistoricCandles)
        await self.session.execute(stmt, historic_candles)
        await self.session.commit()

    async def get_all_historic_candles(self) -> Iterable[HistoricCandles]:
        return await self.all(select(HistoricCandles))
