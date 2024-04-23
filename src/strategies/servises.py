import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

from config import STOCK_MARKET
from repositories.historic_candles import HistoricCandlesRepository
from repositories.security import SecuritiesRepository
from tinkoff.invest import CandleInterval, InstrumentIdType, Share
from tinkoff.invest.async_services import AsyncServices

from strategies.base import get_historic_candle_repository, get_securities_repository, get_tinkoff_client
from strategies.intrevals import interval_dict


# TODO: убрать все print и подумать, как уменьшить число запросов к бирже
class Services:
    def __init__(
        self,
        client: AsyncServices,
        securities_repository: SecuritiesRepository,
        historic_candles_repository: HistoricCandlesRepository,
    ) -> None:
        self.client = client
        self.securities_repo = securities_repository
        self.historic_candles_repo = historic_candles_repository

    async def get_shares(self, ticker: str) -> Share:
        """
        Получает информацию о ценной бумаге по её тикеру.

        :param ticker: Тикер ценной бумаги.
        :type ticker: str
        :return: Информация о ценной бумаге.
        :rtype: Instrument or Exception
        """
        if not STOCK_MARKET:
            raise Exception("STOCK_MARKET is None")

        share = await self.client.instruments.share_by(
            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code=STOCK_MARKET, id=ticker
        )
        return share.instrument

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
            False - Строкое представление времени.
        :return: dict
            Словарь с информацией об инструменте.

        Во избежание превышения лимита запросов внутри присутсвует кулдаун
        """
        size_interval_days = interval_dict[interval]

        share = await self.get_shares("SBER")
        dic = dict()
        dic["figi"] = share.figi
        dic["ticker"] = ticker
        dic["timeframe"] = interval.name
        m = [["time", "open", "close", "high", "low", "volume"]]
        current_date = from_date
        # c = 0
        response = None  # noqa

        while current_date + size_interval_days < to_date:
            response = await self.client.market_data.get_candles(
                figi=share.figi, from_=current_date, to=current_date + size_interval_days, interval=interval
            )

            for i in range(len(response.candles)):
                op = self._cast_money(response.candles[i].open)
                close = self._cast_money(response.candles[i].close)
                high = self._cast_money(response.candles[i].high)
                low = self._cast_money(response.candles[i].low)
                volume = response.candles[i].volume

                if integer_representation_time:  # noqa
                    date = response.candles[i].time.timestamp() * 1000
                else:
                    date = response.candles[i].time

                m.append([date, float(op), float(close), float(high), float(low), float(volume)])  # type: ignore

            current_date += size_interval_days

            #   Кулдаун в целях обхода лимитов на запросы
            # TODO: заменить на глобальный счетчик запросов за минуту
            await asyncio.sleep(0.2)

            #   Счётчик для отображения количества запросов к API
            #   Возможно удаление без последствий
            # c += 1

        response = await self.client.market_data.get_candles(
            figi=share.figi, from_=current_date, to=to_date, interval=interval
        )

        if not response:
            return None
        for i in range(len(response.candles)):
            op = self._cast_money(response.candles[i].open)
            close = self._cast_money(response.candles[i].close)
            high = self._cast_money(response.candles[i].high)
            low = self._cast_money(response.candles[i].low)
            volume = response.candles[i].volume

            if integer_representation_time:  # noqa
                date = response.candles[i].time.timestamp() * 1000
            else:
                date = response.candles[i].time

            m.append([str(date), float(op), float(close), float(high), float(low), float(volume)])  # type: ignore

        dic["history"] = m
        return dic

    @staticmethod
    def _cast_money(v: Any) -> float:
        return v.units + v.nano / 1e9


pass


async def main() -> None:
    from datetime import datetime

    # В API будем через Depends получать. Тут только так(
    client = await anext(get_tinkoff_client)
    securities_repository = await anext(get_securities_repository)
    historic_candles_repository = await anext(get_historic_candle_repository)

    service = Services(client, securities_repository, historic_candles_repository)

    shares = await service.get_historic_candle(
        ticker="SBER",
        from_date=datetime.now(timezone.utc) - timedelta(days=100),
        to_date=datetime.now(timezone.utc),
        interval=CandleInterval.CANDLE_INTERVAL_DAY,
        integer_representation_time=False,
    )
    print(shares)


if __name__ == "__main__":
    asyncio.run(main())
