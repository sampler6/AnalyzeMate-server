import asyncio
import copy
from typing import Dict, List

import numpy as np


class RSI:
    @staticmethod
    def _calculate_rsi(history: List, window: int = 14) -> List[List[float]]:
        """
        Вычисляет индекс относительной силы (RSI) для временного ряда цен.

        :param history: List
            Исторические данные о ценах. Каждый внутренний список содержит два элемента: временную метку и значение цены
        :param window: int
            Размер окна для вычисления RSI (по умолчанию 14).
        :return: List
            Список временных меток и значения RSI.
        """
        time = [entry[0] for entry in history]
        prices = [entry[2] for entry in history]
        rsi_values = []

        deltas = np.diff(prices)
        seed = deltas[:window]
        up = seed[seed >= 0].sum() / window
        down = -seed[seed < 0].sum() / window

        for i, delta in enumerate(deltas[window:], start=window):
            if delta > 0:
                upval = delta
                downval = 0
            else:
                upval = 0
                downval = -delta

            up = (up * (window - 1) + upval) / window
            down = (down * (window - 1) + downval) / window
            rs = up / down
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append([time[i], rsi])

        return rsi_values

    @staticmethod
    def get_rsi(data: Dict, window: int = 14) -> Dict:
        """
        Вычисляет индекс относительной силы (RSI) для временного ряда цен.

        :param data: Dict
             Словарь с данными о бумаге.
        :param window: int
            Размер окна для вычисления RSI (по умолчанию 14).
        :return: Dict
            Словарь с данными о бумаге и RSI.
        """
        rsi_data = [["time", "value"]]
        rsi_data += RSI._calculate_rsi(data["history"][1:], window)  # type: ignore
        result = copy.deepcopy(data)
        result["indicator"] = "RSI"
        result["history"] = rsi_data
        return result

    @staticmethod
    def calculate_rsi_json(data: Dict[str, List[List[float]]], path: str, window: int = 14) -> None:
        """
        Вычисляет индекс относительной силы (RSI) для временного ряда цен и сохраняет его в JSON файл.

        :param data: Dict
             Словарь с данными о бумаге.
        :param window: int
            Размер окна для вычисления RSI (по умолчанию 14).
        :param path: str
            Путь к файлу JSON, в который будет сохранен тренд.
        """
        import json

        rsi = RSI.get_rsi(data, window)
        with open(path, "w") as f:
            json.dump(rsi, f)


async def main() -> None:
    from datetime import datetime, timedelta, timezone

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
        rsi = RSI.get_rsi(shares)
        if rsi is not None:
            indicator = {
                "black": {
                    "history": rsi["history"],
                    "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
                }
            }

            print(rsi)

            graphic.Graphic.print_graphic(shares, indicator)


if __name__ == "__main__":
    asyncio.run(main())
