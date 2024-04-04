import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Any, List

from config import STOCK_MARKET
from tinkoff.invest import CandleInterval, InstrumentIdType
from tinkoff.invest.async_services import AsyncServices

from strategies.base import MAX_INTERVAL_SIZE, get_tinkoff_client


class Services:
    def __init__(self, client: AsyncServices):
        self.client = client

    async def get_shares(self, ticker: str) -> dict:
        """
        Получает информацию о ценной бумаге по её тикеру.

        :param ticker: Тикер ценной бумаги.
        :type ticker: str
        :return: dict
            - ticker: string Тикер
            - name: string Эмитент
            - lot: int Лотность
            - min_price_increment: double Минимальный шаг цены
            - currency: string Валюта
            - country: string Страна
            - sector: string Сектор деятельности
            - liquidity: bool
                True - Бумага ликвидна
                False - Бумага не ликвидна
            Информация о ценной бумаге.
        :rtype: Instrument or Exception
        """
        responce = await self.client.instruments.share_by(
            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code=STOCK_MARKET, id=ticker
        )
        share = {
            "ticker": responce.instrument.ticker,
            "name": responce.instrument.name,
            "lot": responce.instrument.lot,
            "currency": responce.instrument.currency,
            "country": responce.instrument.country_of_risk_name,
            "sector": responce.instrument.sector,
            "min_price_increment": responce.instrument.min_price_increment,
            "liquidity": responce.instrument.liquidity_flag,
        }
        return share

    async def get_shares_json(self, ticker: str, path: str) -> None:
        """
        Получает информацию о ценной бумаге по её тикеру и сохраняет её в JSON файл.

        :param ticker: Тикер ценной бумаги.
        :type ticker: str
        :param path: Путь к файлу JSON, в который будет сохранена информация о ценной бумаге.
        :type path: str
        """
        share = await self.get_shares(ticker)
        with open(path, "w") as f:  # noqa
            json.dump(share, f)

    async def _get_candles(
        self,
        figi: str,
        from_date: datetime,
        to_date: datetime,
        interval: CandleInterval,
        integer_representation_time: bool,
    ) -> List[List[float]]:
        """
        Получает исторические данные свечей для заданного тикера и временного интервала.
        :param figi: str
            FIGI инструмента.
        :param from_date: datetime.datetime
            Начальная дата и время периода.
        :param to_date: datetime.datetime
            Конечная дата и время периода.
        :param interval: enum CandleInterval
            Временной интервал свечей (CandleInterval).
        :param integer_representation_time: bool
            True - Десятичное представление времени(мс)
            False - Строкое представление времени.
        :return: list
            Список с информацией о свечах.
        """
        array_candles = []
        response = await self.client.market_data.get_candles(figi=figi, from_=from_date, to=to_date, interval=interval)

        for i in range(len(response.candles)):
            open_price = self._cast_money(response.candles[i].open)
            close_price = self._cast_money(response.candles[i].close)
            high_price = self._cast_money(response.candles[i].high)
            low_price = self._cast_money(response.candles[i].low)
            volume = response.candles[i].volume

            if integer_representation_time:  # noqa
                date = int(response.candles[i].time.timestamp() * 1000)
            else:
                date = response.candles[i].time

            array_candles.append(
                [date, float(open_price), float(close_price), float(high_price), float(low_price), float(volume)]
            )  # type: ignore

        return array_candles

    async def get_historic_candle(
        self,
        ticker: str,
        from_date: datetime,
        to_date: datetime,
        interval: CandleInterval,
        integer_representation_time: bool,
    ) -> dict | None:
        """
        Получает исторические данные свечей для заданного тикера и временного интервала.
        :param ticker: str
            Тикер инструмента.
        :param from_date: datetime.datetime
            Начальная дата и время периода.
        :param to_date: datetime.datetime
            Конечная дата и время периода.
        :param interval: enum CandleInterval
            Временной интервал свечей (CandleInterval).
        :param integer_representation_time: bool
            True - Десятичное представление времени(мс)
            False - Строковое представление времени.
        :return: dict
            Словарь с информацией об инструменте.

        Во избежание превышения лимита запросов внутри присутсвует кулдаун
        """
        share = await self.client.instruments.share_by(
            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code=STOCK_MARKET, id=ticker
        )
        size_interval_days = MAX_INTERVAL_SIZE[interval]
        if (from_date < share.instrument.first_1min_candle_date and size_interval_days < timedelta(days=1)) or (
            from_date < share.instrument.first_1day_candle_date
        ):
            raise AttributeError("За указанный период отсутсвуют данные о свечах")

        dic = dict()
        dic["ticker"] = ticker
        dic["timeframe"] = interval.name
        array_candles = [["time", "open", "close", "high", "low", "volume"]]
        current_date = from_date

        while current_date + size_interval_days < to_date:
            array_candles += await self._get_candles(
                figi=share.instrument.figi,
                from_date=current_date,
                to_date=current_date + size_interval_days,
                interval=interval,
                integer_representation_time=integer_representation_time,
            )  # type: ignore

            current_date += size_interval_days  # type: ignore

            #   Кулдаун в целях обхода лимитов на запросы
            await asyncio.sleep(0.2)

        array_candles += await self._get_candles(
            figi=share.instrument.figi,
            from_date=current_date,
            to_date=to_date,
            interval=interval,
            integer_representation_time=integer_representation_time,
        )  # type: ignore

        dic["history"] = array_candles  # type: ignore
        return dic

    async def get_historic_candle_json(
        self,
        ticker: str,
        path: str,
        from_date: datetime,
        to_date: datetime,
        interval: CandleInterval,
        integer_representation_time: bool,
    ) -> None:
        """
        Получает исторические данные свечей для заданного тикера и временного интервала и сохраняет их в JSON файл.

        :param ticker: str
            Тикер инструмента.
        :param path: str
            Путь к файлу JSON, в который будет сохранен результат.
        :param from_date: datetime.datetime
            Начальная дата и время периода.
        :param to_date: datetime.datetime
            Конечная дата и время периода.
        :param interval: enum CandleInterval
            Временной интервал свечей (CandleInterval).
        :param integer_representation_time: bool
            True - Десятичное представление времени(мс)
            False - Строковое представление времени.
        """
        candle_data = await self.get_historic_candle(
            ticker=ticker,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
            integer_representation_time=integer_representation_time,
        )
        with open(path, "w") as f:  # noqa
            json.dump(candle_data, f)

    @staticmethod
    def _cast_money(v: Any) -> float:
        return v.units + v.nano / 1e9


pass


async def main() -> None:
    from datetime import datetime, timedelta

    # В API будем через Depends получать. Тут только так(
    client = await anext(get_tinkoff_client)

    service = Services(client)

    shares = await service.get_historic_candle(
        ticker="SBER",
        from_date=datetime.now(timezone.utc) - timedelta(days=400),
        to_date=datetime.now(timezone.utc),
        interval=CandleInterval.CANDLE_INTERVAL_DAY,
        integer_representation_time=False,
    )
    print(shares)


if __name__ == "__main__":
    asyncio.run(main())
