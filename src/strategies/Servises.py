from time import sleep
from datetime import timedelta
from tinkoff.invest import Client, InstrumentIdType, CandleInterval
from config import TOKEN, STOCK_MARKET
class Services:

    @staticmethod
    def GetShares(Ticker):
        """
        Получает информацию о ценной бумаге по её тикеру.

        :param Ticker: Тикер ценной бумаги.
        :type Ticker: str
        :return: Информация о ценной бумаге.
        :rtype: Instrument or Exception
        """
        with Client(TOKEN) as client:
            try:
                share = client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                                                    class_code=STOCK_MARKET, id=Ticker)
                return share.instrument
            except:
                return Exception("Отсутсвует бумага с указанным  тикером")

    @staticmethod
    def GetHistoricCandle(Ticker, From, To, Interval, IntegerRepresentationTime):
        """
        Получает исторические данные свечей для заданного тикера и временного интервала.
        :param Token: str
            Ключ доступа (токен) к API Tinkoff Invest.
        :param Ticker: str
            Тикер инструмента.
        :param From: datetime.datetime
            Начальная дата и время периода.
        :param To: datetime.datetime
            Конечная дата и время периода.
        :param Interval: enum CandleInterval
            Временной интервал свечей (CandleInterval).
        :param IntegerRepresentationTime: bool
            True - Десятичное представление времени(мс)
            False - Строкое представление времени.
        :return: dict
            Словарь с информацией об инструменте.

        Во избежание превышения лимита запросов внутри присутсвует кулдаун
        """
        sizeIntervalDays = timedelta(days=0)
        if Interval == CandleInterval.CANDLE_INTERVAL_1_MIN:
            sizeIntervalDays = timedelta(days=1)
        elif Interval == CandleInterval.CANDLE_INTERVAL_2_MIN:
            sizeIntervalDays = timedelta(days=1)
        elif Interval == CandleInterval.CANDLE_INTERVAL_3_MIN:
            sizeIntervalDays = timedelta(days=1)
        elif Interval == CandleInterval.CANDLE_INTERVAL_5_MIN:
            sizeIntervalDays = timedelta(days=1)
        elif Interval == CandleInterval.CANDLE_INTERVAL_10_MIN:
            sizeIntervalDays = timedelta(days=1)
        elif Interval == CandleInterval.CANDLE_INTERVAL_15_MIN:
            sizeIntervalDays = timedelta(days=1)
        elif Interval == CandleInterval.CANDLE_INTERVAL_30_MIN:
            sizeIntervalDays = timedelta(days=2)
        elif Interval == CandleInterval.CANDLE_INTERVAL_HOUR:
            sizeIntervalDays = timedelta(days=7)
        elif Interval == CandleInterval.CANDLE_INTERVAL_4_HOUR:
            sizeIntervalDays = timedelta(days=31)
        elif Interval == CandleInterval.CANDLE_INTERVAL_DAY:
            sizeIntervalDays = timedelta(days=366)
        elif Interval == CandleInterval.CANDLE_INTERVAL_WEEK:
            sizeIntervalDays = timedelta(days=732)
        elif Interval == CandleInterval.CANDLE_INTERVAL_MONTH:
            sizeIntervalDays = timedelta(days=3660)

        with Client(TOKEN) as client:
            share = Services.GetShares("SBER")
            dic = {}
            dic["figi"] = share.figi
            dic["ticker"] = Ticker
            dic["timeframe"] = str(Interval).split(".")[1]
            m = [["time", "open", "close", "high", "low", "volume"]]
            currentDate = From
            c = 0
            while (currentDate + sizeIntervalDays < To):
                r = client.market_data.get_candles(
                    figi=share.figi,
                    from_=currentDate,
                    to=currentDate + sizeIntervalDays,
                    interval=Interval
                )

                for i in range(len(r.candles)):
                    op = Services._cast_money(r.candles[i].open)
                    close = Services._cast_money(r.candles[i].close)
                    high = Services._cast_money(r.candles[i].high)
                    low = Services._cast_money(r.candles[i].low)
                    volume = r.candles[i].volume

                    if IntegerRepresentationTime:
                        date = (r.candles[i].time).timestamp() * 1000
                    else:
                        date = r.candles[i].time

                    m.append([date, op, close, high, low, volume])

                currentDate += sizeIntervalDays

                #   Кулдаун в целях обхода лимитов на запросы
                sleep(0.2)

                #   Счётчик для отображения количества запросов к API
                #   Возможно удаление без последствий
                print(c)
                c += 1

            r = client.market_data.get_candles(
                figi=share.figi,
                from_=currentDate,
                to=To,
                interval=Interval
            )

            for i in range(len(r.candles)):
                op = Services._cast_money(r.candles[i].open)
                close = Services._cast_money(r.candles[i].close)
                high = Services._cast_money(r.candles[i].high)
                low = Services._cast_money(r.candles[i].low)
                volume = r.candles[i].volume

                if IntegerRepresentationTime:
                    date = (r.candles[i].time).timestamp() * 1000
                else:
                    date = r.candles[i].time

                m.append([date, op, close, high, low, volume])

            dic["history"] = m
        return dic

    @staticmethod
    def _cast_money(v):
        return v.units + v.nano / 1e9
pass

if __name__ == "__main__":
    from datetime import datetime, timedelta
    shares = Services.GetHistoricCandle(Ticker="SBER", From=datetime.utcnow() - timedelta(days=1000),
                                        To=datetime.utcnow(), Interval=CandleInterval.CANDLE_INTERVAL_DAY,
                                        IntegerRepresentationTime=False)
    print(shares)