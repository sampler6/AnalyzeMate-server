from db.base_repository import BaseRepository
from securities.models import HistoricCandles
from securities.schemas import HistoricCandlesSchema


class HistoricCandlesRepository(BaseRepository):
    async def save_historic_candle(self, historic_candle: HistoricCandlesSchema) -> None:
        historic_candle_db = HistoricCandles(**historic_candle.model_dump())

        await self.save(historic_candle_db)
        await self.session.commit()

    async def save_historic_candles(self, historic_candles: list[HistoricCandlesSchema]) -> None:
        historic_candles_db: list[HistoricCandles] = list()
        for historic_candle in historic_candles:
            historic_candles_db.append(HistoricCandles(**historic_candle.model_dump()))

        await self.save_all(historic_candles_db)
        await self.session.commit()
