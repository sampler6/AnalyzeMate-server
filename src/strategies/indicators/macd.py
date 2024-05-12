import asyncio
from datetime import datetime
from typing import Dict, List

from strategies.indicators.ema import EMA


class MACD:
    @staticmethod
    async def calculate_macd(
        data: Dict[str, List[List[float]]], short_period: int = 12, long_period: int = 26, signal_period: int = 9
    ) -> None:
        """
        Вычисляет индикатор MACD (Moving Average Convergence Divergence) для временного ряда цен.

        :param data: Словарь с данными, содержащий исторические цены.
        :param short_period: Краткий период для вычисления короткого EMA (по умолчанию 12).
        :param long_period: Длинный период для вычисления длинного EMA (по умолчанию 26).
        :param signal_period: Период для вычисления сигнальной линии (по умолчанию 9).
        :return: Список кортежей, содержащих временные метки, значения MACD Line, Signal Line и Histogram.
        """
        history = data["history"][1:]  # пропускаем строку заголовков
        time = [entry[0] for entry in history]
        prices = [entry[2] for entry in history]  # noqa
        # macd_values: List[Tuple[Union[str, datetime], float, float, float]] = []

        # Вычисляем EMA для короткого периода
        short_ema = EMA.get_ema(data, short_period)

        # Вычисляем EMA для длинного периода
        long_ema = EMA.get_ema(data, long_period)

        # Вычисляем разницу между коротким и длинным EMA (MACD Line)
        macd_line = []
        for i in range(len(short_ema)):
            macd_line.append([time[i], short_ema[i][1] - long_ema[i][1]])

        # # Вычисляем сигнальную линию (EMA от MACD Line)
        # signal_line = Indicators.calculate_ema(macd_line, signal_period)
        #
        # # Вычисляем гистограмму (разница между MACD Line и сигнальной линией)
        # histogram = macd_line[len(long_ema) - len(signal_line):] - signal_line
        #
        # # Собираем результаты в список кортежей
        # for i in range(len(histogram)):
        #     macd_values.append((time[i + long_period - 1], macd_line[i], signal_line[i], histogram[i]))
        #
        # return macd_values


async def main() -> None:
    from datetime import timedelta, timezone

    from tinkoff.invest import CandleInterval

    from strategies import graphic
    from strategies.base import get_tinkoff_client
    from strategies.indicators.trend import Trend
    from strategies.servises import Services

    # В API будем через Depends получать. Тут только так(
    client = await anext(get_tinkoff_client)

    service = Services(client)
    shares = await service.get_historic_candle(
        ticker="SBER",
        from_date=datetime.now(timezone.utc) - timedelta(days=1000),
        to_date=datetime.now(timezone.utc),
        interval=CandleInterval.CANDLE_INTERVAL_DAY,
        integer_representation_time=False,
    )

    if shares is not None:
        trend = Trend.get_trend(shares)
        if trend is not None:
            indicator = {
                "black": {
                    "history": trend,
                    "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
                }
            }

            print(trend)

            graphic.Graphic.print_graphic(shares, indicator)  # type: ignore


if __name__ == "__main__":
    asyncio.run(main())
