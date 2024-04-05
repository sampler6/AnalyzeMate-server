import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import graphic
import numpy as np
from servises import Services
from tinkoff.invest import CandleInterval

from strategies.base import get_historic_candle_repository, get_securities_repository, get_tinkoff_client
from strategies.intrevals import angle_inclination, size_trend_window


class Indicators:
    @staticmethod
    def calculate_trend(data: Dict[str, List[List[float]]]) -> List[List[float]]:
        """
        Вычисляет тренд на основе временного ряда цен.
        :param data: dict
            Словарь с данными, содержащий исторические цены.
        :return: list
            Список списков, содержащий временные метки и значения тренда.
        """
        history = data["history"][1:]  # пропускаем строку заголовков
        time = [entry[0] for entry in history]
        prices = [(entry[1] + entry[2]) / 2 for entry in history]
        trends = []

        for i in range(0, len(prices), size_trend_window):
            # Индексы для текущего окна размером 10
            indices = list(range(i, min(i + size_trend_window, len(prices))))
            x = np.arange(len(indices))  # Создание массива индексов
            y = np.array(prices[i : i + size_trend_window])  # Получение значений цен для текущего окна
            A = np.vstack([x, np.ones(len(x))]).T  # Построение матрицы для аппроксимации
            slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]  # Линейная аппроксимация
            if slope > angle_inclination:
                trends.append([time[indices[0]], prices[indices[0]], "Up", slope])  # Сохранение коэффициента наклона
            elif slope < -angle_inclination:
                trends.append([time[indices[0]], prices[indices[0]], "Down", slope])  # Сохранение коэффициента наклона
            else:
                trends.append([time[indices[0]], prices[indices[0]], "Row", slope])  # Сохранение коэффициента наклона

        flag_check_order = True
        while flag_check_order:
            flag_check_order = False
            i = 1
            while i < len(trends):
                if trends[i - 1][2] == trends[i][2]:
                    trends.remove(trends[i])
                    flag_check_order = True
                    continue
                i += 1

        result = [["time", "value"]]
        for i in range(len(trends)):
            result.append([trends[i][0], trends[i][1]])

        return result  # type: ignore

    @staticmethod
    def calculate_trend_json(data: Dict[str, List[List[float]]], path: str) -> None:
        """
        Вычисляет тренд на основе временного ряда цен и сохраняет его в JSON файл.
        :param data: dict
            Словарь с данными, содержащий исторические цены.
        :param path: str
            Путь к файлу JSON, в который будет сохранен тренд.
        """
        trend = Indicators.calculate_trend(data)
        with open(path, "w") as f:
            json.dump(trend, f)

    @staticmethod
    def calculate_rsi(data: Dict[str, List[List[float]]], window: int) -> Dict[str, any]:  # type: ignore
        # Данный метод находится в процессе написания. Проверка не требуется
        """
        Вычисляет индикатор относительной силы (RSI) на основе исторических данных цен.
        :param data: dict
            Словарь с данными, содержащий исторические цены.
        :param window: int
            Размер окна для вычисления RSI.
        :return: dict
            Словарь с информацией об индикаторе RSI.
        """

        history = data["history"][1:]  # пропускаем строку заголовков
        time = [entry[0] for entry in history]
        close_prices = [entry[2] for entry in history]
        ema_values = []
        alpha = 2 / (window + 1)  # Коэффициент сглаживания

        # Вычисление начального значения EMA (простое скользящее среднее первых window значений)
        sma = sum(close_prices[:window]) / window
        ema_values.append(sma)

        # Словарь для хранения результата
        result = {
            "figi": data["figi"],
            "ticker": data["ticker"],
            "timeframe": data["timeframe"],
            "indicator": "EMA",
            "history": [["time", "value"]],
        }

        # Вычисление EMA для остальных точек
        for i in range(window, len(close_prices)):
            ema = (close_prices[i] - ema_values[-1]) * alpha + ema_values[-1]
            ema_values.append(ema)
            result["history"].append([time[i], ema])  # type: ignore

        return result


async def main() -> None:
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

    a = Indicators.calculate_trend(shares)
    indicator = {
        "black": {
            "history": a,
            "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
        }
    }

    graphic.Graphic.print_graphic(shares, indicator)
    print(a)


if __name__ == "__main__":
    asyncio.run(main())
