import asyncio
import copy
from datetime import datetime
from typing import Any, Dict, List

from strategies.indicators.ema import EMA


class MACD:
    @staticmethod
    def calculate_macd(
        data: Dict[str, List[List[Any]]], short_period: int = 12, long_period: int = 26, signal_period: int = 9
    ) -> Dict | None:
        """
        Вычисляет индикатор MACD (Moving Average Convergence Divergence) для временного ряда цен.

        :param data: dict{"history": [[datetime, float]]}
            Словарь с данными, содержащий исторические цены.
        :param short_period: int
            Краткий период для вычисления короткого EMA (по умолчанию 12).
        :param long_period: int
            Длинный период для вычисления длинного EMA (по умолчанию 26).
        :param signal_period: int
            Период для вычисления сигнальной линии (по умолчанию 9).
        :return: dict{"history": [[datetime, float]]}
            Словарь с данными о бумаге и значениями MACD Line, Signal Line и Histogram.
        """
        history = data["history"][1:]  # пропускаем строку заголовков
        time = [entry[0] for entry in history]
        prices = [entry[2] for entry in history]  # noqa

        # Вычисляем EMA для короткого периода
        short_ema = list(EMA.get_ema(data, short_period)["history"][1:])

        # Вычисляем EMA для длинного периода
        long_ema = list(EMA.get_ema(data, long_period)["history"][1:])

        while short_ema[0][0] != long_ema[0][0]:
            short_ema.remove(short_ema[0])
        # Вычисляем разницу между коротким и длинным EMA (MACD Line)
        macd_line = [["time", "value"]]
        for i in range(len(short_ema)):
            macd_line.append([time[i], short_ema[i][1] - long_ema[i][1]])

        data_signal = copy.deepcopy(data)
        data_signal["history"] = macd_line

        # Вычисляем сигнальную линию (EMA от MACD Line)
        signal_line = EMA.get_ema(data_signal, signal_period)["history"]

        while macd_line[1][0] != signal_line[1][0]:
            macd_line.remove(macd_line[1])
        # Вычисляем гистограмму (разница между MACD Line и сигнальной линией)
        histogram = [["time", "value"]]
        for i in range(1, len(macd_line)):
            macd_value = float(macd_line[i][1])  # Convert MACD value to float
            signal_value = float(signal_line[i][1])  # Convert signal value to float
            histogram_value = macd_value - signal_value
            histogram.append([time[i], histogram_value])  # type: ignore

        macd_values = [["time", "macd_line", "signal_line", "historgam"]]

        while histogram[1][0] != signal_line[1][0]:
            histogram.remove(histogram[1])
        # Собираем результаты в список кортежей
        for i in range(1, len(histogram)):
            macd_values.append([time[i + long_period - 1], macd_line[i][1], signal_line[i][1], histogram[i][1]])

        data_signal["history"] = macd_values
        data_signal["indicator"] = "macd"  # type: ignore
        return data_signal


async def main() -> None:
    from datetime import timedelta, timezone

    from tinkoff.invest import CandleInterval

    from strategies import graphic
    from strategies.base import get_historic_candle_repository, get_securities_repository, get_tinkoff_client
    from strategies.servises import Services

    # В API будем через Depends получать. Тут только так(
    client = await anext(get_tinkoff_client)
    securities_repository = await anext(get_securities_repository)
    historic_candles_repository = await anext(get_historic_candle_repository)

    service = Services(client, securities_repository, historic_candles_repository)
    shares = await service.get_historic_candle(
        ticker="SBER",
        from_date=datetime.now(timezone.utc) - timedelta(days=1000),
        to_date=datetime.now(timezone.utc),
        interval=CandleInterval.CANDLE_INTERVAL_DAY,
        integer_representation_time=False,
    )

    if shares is not None:
        macd = MACD.calculate_macd(shares)
        if macd is not None:
            history = macd["history"]
            line = []
            for i in range(len(history)):
                line.append([history[i][0], history[i][1]])
            indicator = {
                "black": {
                    "history": line,
                    "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
                }
            }
            line = []
            for i in range(len(history)):
                line.append([history[i][0], history[i][2]])
            indicator["red"] = {
                "history": line,
                "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
            }
            line = []
            for i in range(len(history)):
                line.append([history[i][0], history[i][3]])
            indicator["blue"] = {
                "history": line,
                "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
            }

            graphic.Graphic.print_graphic(shares, indicator)  # type: ignore


if __name__ == "__main__":
    asyncio.run(main())
