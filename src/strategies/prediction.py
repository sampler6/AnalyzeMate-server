import asyncio
import sys
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Dict, List

import numpy as np
from tinkoff.invest import CandleInterval

from strategies.base import get_tinkoff_client


class Prediction:
    @staticmethod
    def get_trend_predict(data: Dict[str, List[List[float]]]) -> Dict | None:
        """
        Даёт прогноз на основании тренда
        :param data: dict{"history": [[datetime, float]]}
            Словарь с данными о бумаге.
        :return: dict{"id": int, "ticker": str, "open": float, "close": float, "take profit": float}
            Параметры сделки.
        """
        from strategies.indicators.trend import Trend
        from strategies.settings_strategies import angle_inclination, broker_commission, interval_order_in_trend

        history = data["history"][1:]  # пропускаем строку заголовков
        time = [entry[0] for entry in history]
        # open_prices = [entry[1] for entry in history]
        # close_prices = [entry[2] for entry in history]
        # hight_prices = [entry[3] for entry in history]
        # low_prices = [entry[4] for entry in history]
        # volume = [entry[5] for entry in history]
        average_prices = [(entry[1] + entry[2]) / 2 for entry in history]

        trends = Trend.get_trend(data)
        list_trend = trends["history"][1:]

        array_delta_max = []
        array_delta_min = []
        theory_size = 0.0
        slope = 0.0

        # Получаем списки самых сильных отклонений реальных значений от тренда
        for i in range(len(list_trend) - 1):
            y = np.array(
                average_prices[time.index(list_trend[i][0]) : time.index(list_trend[i + 1][0])]
            )  # Получение значений цен для текущего окна
            x = np.arange(len(y))  # Создание массива индексов
            A = np.vstack([x, np.ones(len(x))]).T  # Построение матрицы для аппроксимации
            slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]  # Линейная аппроксимация

            delta_max = 0.0
            delta_min = 0.0
            last_element_trends = time.index(list_trend[-1][0])
            theory_size = average_prices[last_element_trends]
            for j in range(last_element_trends, len(time)):
                if history[j][3] - theory_size > delta_max:
                    delta_max = history[j][3] - theory_size
                if theory_size - history[j][4] > delta_min:
                    delta_min = theory_size - history[j][4]
                theory_size += slope
            array_delta_max.append(delta_max)
            array_delta_min.append(delta_min)

        # TODO: хз, почему тут пропадает значение
        # Берём среднее значение
        delta_min = 0
        if array_delta_min != []:
            delta_min = mean(array_delta_min)
        delta_max = 0
        if array_delta_max != []:
            delta_max = mean(array_delta_max)

        # Выставляем параметры сделки
        if average_prices[-1] < theory_size - delta_min * interval_order_in_trend and slope > angle_inclination:
            take_profit = theory_size + delta_max * interval_order_in_trend
            open = history[-1][2]
            close = open - delta_min * interval_order_in_trend
            if open <= close:
                return None
            ticker = data["ticker"]
            id = 1
            if open * (1 + 2 * broker_commission) < take_profit:
                return {"id": id, "ticker": ticker, "open": open, "close": close, "take profit": take_profit}

        return None

    @staticmethod
    def get_RSI_predict(data: Dict[str, List[List[float]]]) -> Dict | None:
        """
        Даёт прогноз на основании EMA
        :param data: dict{"history": [[datetime, float]]}
            Словарь с данными о бумаге.
        :return: dict{"id": int, "ticker": str, "open": float, "close": float, "take profit": float}
            Параметры сделки.
        """
        from strategies.indicators.rsi import RSI
        from strategies.settings_strategies import broker_commission, lower_value_EMA, upper_value_EMA, window_EMA

        history = data["history"][1:]  # пропускаем строку заголовков
        # time = [entry[0] for entry in history]
        # open_prices = [entry[1] for entry in history]
        # close_prices = [entry[2] for entry in history]
        # hight_prices = [entry[3] for entry in history]
        # low_prices = [entry[4] for entry in history]
        # volume = [entry[5] for entry in history]
        # average_prices = [(entry[1] + entry[2]) / 2 for entry in history]

        # Получаем значение RSI
        rsi = RSI.get_rsi(data)
        list_rsi_size = rsi["history"][1:]

        # Берём последний значение перекупленности
        take_element = []
        if list_rsi_size[-1][1] <= lower_value_EMA:
            for i in range(len(list_rsi_size) - 1, 0, -1):
                if list_rsi_size[i][1] >= upper_value_EMA:
                    take_element = list_rsi_size[i]
                    break

        if len(take_element) == 0:
            return None

        # Рассчитываем значения сделки
        for i in range(len(history) - 1, 0, -1):
            if take_element[0] == history[i][0]:
                take_element = history[i]
                ticker = rsi["ticker"]
                id = 1
                take_profit = (take_element[1] + take_element[2]) / 2
                open = history[-1][3]

                close = sys.maxsize + 0.0
                for j in range(window_EMA, 0, -1):
                    if i - j >= 0 and history[i - j][4] < close:
                        close = history[i - j][4]

                if open > close * (1 + 2 * broker_commission) and open * (1 + 2 * broker_commission) < take_profit:
                    return {"id": id, "ticker": ticker, "open": open, "close": close, "take profit": take_profit}
                else:
                    return None

        # if average_prices[-1] < theory_size - delta_min * interval_order_in_trend and slope > angle_inclination:
        #     take_profit = theory_size + delta_max * interval_order_in_trend
        #     open = history[-1][2]
        #     close = open - delta_min * interval_order_in_trend
        #     if open <= close:
        #         return None
        #     ticker = data["ticker"]
        #     id = 1
        #     if open * (1 + 2 * broker_commission) < take_profit:
        #         return {"id": id, "ticker": ticker, "open": open, "close": close, "take profit": take_profit}

        return None


async def trend_predict() -> None:
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

    # trend = Trend.get_trend(shares)
    # ema = EMA.get_ema(shares, window_EMA)
    # rsi = RSI.get_rsi(shares, 14)
    # indicator = {
    #     "black": {
    #         "history": trend["history"][1:],
    #         "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
    #     }
    # }

    # graphic.Graphic.print_graphic(shares, indicator)
    if shares is not None:
        a = Prediction.get_trend_predict(shares)

        if a is not None:
            print(
                f"id: {a["id"]}\nticker: {a["ticker"]}\nopen: {a["open"]}\nclose: {a["close"]}\ntake profit: "
                f"{a["take profit"]}"
            )


async def ema_predict() -> None:
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

    # trend = Trend.get_trend(shares)
    # ema = EMA.get_ema(shares, window_EMA)
    # rsi = RSI.get_rsi(shares, 14)
    # indicator = {
    #     "black": {
    #         "history": trend["history"][1:],
    #         "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
    #     }
    # }

    # graphic.Graphic.print_graphic(shares, indicator)
    if shares is not None:
        a = Prediction.get_RSI_predict(shares)

        if a is not None:
            print(
                f"id: {a["id"]}\nticker: {a["ticker"]}\nopen: {a["open"]}\nclose: {a["close"]}\ntake profit: "
                f"{a["take profit"]}"
            )


if __name__ == "__main__":
    # asyncio.run(trend_predict())
    asyncio.run(ema_predict())
