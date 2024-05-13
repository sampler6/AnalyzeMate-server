import asyncio
import copy
from typing import Dict, List

import numpy as np

from strategies.settings_strategies import angle_inclination, share_wave, size_trend_window


class Trend:
    @staticmethod
    def _calculate_trend(history: List[List[float]]) -> List[List[float]]:
        """
        Вычисляет тренд на основе временного ряда цен.

        :param history: List[[datetime, float]]
            Исторические данные о ценах. Каждый внутренний список содержит два элемента: временную метку и значение цены
        :return: List[[datetime, float]]
            Список временных меток и значения тренда.
        """
        time = [entry[0] for entry in history]  # временные метки
        prices = [(entry[1] + entry[2]) / 2 for entry in history]  # значения цен
        trends = []

        # Проводим линейную регрессию на маленьких участках
        for i in range(0, len(prices), size_trend_window):
            # Индексы для текущего окна
            indices = list(range(i, min(i + size_trend_window, len(prices))))
            x = np.arange(len(indices))  # Создание массива индексов
            y = np.array(prices[i : i + size_trend_window])  # Получение значений цен для текущего окна
            A = np.vstack([x, np.ones(len(x))]).T  # Построение матрицы для аппроксимации
            slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]  # Линейная аппроксимация
            if slope > angle_inclination:
                trends.append(
                    [time[indices[0]], prices[indices[0]], "Up", 1, slope, intercept]
                )  # Сохранение коэффициента наклона
            elif slope < -angle_inclination:
                trends.append(
                    [time[indices[0]], prices[indices[0]], "Down", 1, slope, intercept]
                )  # Сохранение коэффициента наклона
            else:
                trends.append(
                    [time[indices[0]], prices[indices[0]], "Row", 1, slope, intercept]
                )  # Сохранение коэффициента наклона

        # Пока происходят изменения
        flag_check_order = True
        while flag_check_order:
            flag_check_order = False

            # Если два смежных участка имеют одинаковый тренд, то объединяем их
            i = 1
            while i < len(trends):
                if trends[i - 1][2] == trends[i][2]:
                    trends[i - 1][3] += trends[i][3]
                    trends.remove(trends[i])
                    flag_check_order = True
                    continue
                i += 1

            # Если из трех участков первый и последний имеют одинаковый тренд и в сумме значительно больше по длинне,
            # чем центральный участок, то объединяем все 3 участка
            i = 1
            while i < len(trends) - 2:
                if trends[i - 1][2] == trends[i + 1][2] and (
                    (trends[i - 1][3] + trends[i + 1][3]) * share_wave > trends[i][3]
                ):
                    trends[i - 1][3] += trends[i][3] + trends[i + 1][3]
                    trends.remove(trends[i + 1])
                    trends.remove(trends[i])
                    flag_check_order = True
                    continue
                else:
                    i += 1

        result = []
        for i in range(len(trends)):
            result.append([trends[i][0], trends[i][1]])

        return result

    @staticmethod
    def get_trend(data: Dict) -> Dict:
        """
        Вычисляет тренд на основе временного ряда цен.
        :param data: dict{"history": [[datetime, float]]}
            Словарь с данными о бумаге.
        :return: dict{"history": [[datetime, float]]}
            Словарь с данными о бумаге и тренде.
        """
        trend = [["time", "value"]]
        trend += Trend._calculate_trend(data["history"][1:])  # type: ignore
        result = copy.deepcopy(data)
        result["indicator"] = "Trend"
        result["history"] = trend
        return result

    @staticmethod
    def calculate_trend_json(data: Dict, path: str) -> None:
        """
        Вычисляет тренд на основе временного ряда цен и сохраняет его в JSON файл.

        :param data: dict{"history": [[datetime, float]]}
            Словарь с данными о бумаге.
        :param path: str
            Путь к файлу JSON, в который будет сохранен тренд.
        """
        import json

        with open(path, "w") as f:
            json.dump(Trend.get_trend(data), f)


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
        ticker="ABIO",
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
                    "history": trend["history"],
                    "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
                }
            }

            print(trend)

            graphic.Graphic.print_graphic(shares, indicator)


if __name__ == "__main__":
    asyncio.run(main())
