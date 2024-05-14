import asyncio
import copy
from typing import Dict, List


class EMA:
    @staticmethod
    def _calculate_ema(history: List, window: int = 14) -> List:
        """
        Вычисляет экспоненциальное скользящее среднее (EMA) на основе исторических данных.

        :param history: list[[datetime, float]]
            Исторические данные о ценах. Каждый внутренний список содержит два элемента: временную метку и значение цены
        :param window: int
            Размер окна для вычисления EMA.
        :return: list[[datetime, float]]
            Список временных меток и значения EMA.
        """
        time = [entry[0] for entry in history]
        prices = [entry[2] if len(history[0]) > 2 else entry[1] for entry in history]

        ema_values = []

        # Вычисляем начальное значение EMA как простое скользящее среднее для первых window точек
        initial_ema = sum(prices[:window]) / window
        ema_values.append([time[window - 1], initial_ema])

        # Вычисляем остальные значения EMA с использованием формулы экспоненциального сглаживания
        for i in range(window, len(prices)):
            ema = (prices[i] - ema_values[-1][1]) * (2 / (window + 1)) + ema_values[-1][1]
            ema_values.append([time[i], ema])

        return ema_values

    @staticmethod
    def get_ema(data: Dict, window: int = 14) -> Dict:
        """
        Вычисляет экспоненциальное скользящее среднее (EMA) на основе временного ряда цен.

        :param data: dict{"history": [[datetime, float]]}
            Словарь с данными о бумаге.
        :param window: int
            Размер окна для вычисления EMA.
        :return: dict{"history": [[datetime, float]]}
            Словарь с данными о бумаге и EMA.
        """
        ema = [["time", "value"]]
        ema += EMA._calculate_ema(data["history"][1:], window)
        result = copy.deepcopy(data)
        result["indicator"] = "EMA"
        result["history"] = ema
        return result

    @staticmethod
    def calculate_ema_json(data: Dict, path: str, window: int = 14) -> None:
        """
        Вычисляет экспоненциальное скользящее среднее (EMA) на основе временного ряда цен
        и сохраняет его в JSON файл.

        :param data: dict{"history": [[datetime, float]]}
            Словарь с данными о бумаге.
        :param window: int
            Размер окна для вычисления EMA.
        :param path: str
            Путь к файлу JSON, в который будет сохранен EMA.
        """
        import json

        ema = EMA.get_ema(data, window)
        with open(path, "w") as f:
            json.dump(ema, f)


async def main() -> None:
    from datetime import datetime, timedelta, timezone

    from tinkoff.invest import CandleInterval

    from strategies import graphic
    from strategies.base import get_tinkoff_client
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
        ema = EMA.get_ema(shares)
        if ema is not None:
            indicator = {
                "black": {
                    "history": ema["history"],
                    "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
                }
            }

            print(ema)

            graphic.Graphic.print_graphic(shares, indicator)


if __name__ == "__main__":
    asyncio.run(main())
