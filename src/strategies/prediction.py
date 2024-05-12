import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import numpy as np
from tinkoff.invest import CandleInterval

from strategies.base import get_tinkoff_client
from strategies.indicators.trend import Trend
from strategies.servises import Services
from strategies.settings_strategies import broker_commission, interval_order_in_trend


class Prediction:
    @staticmethod
    def get_trend_predict(data: Dict[str, List[List[float]]]) -> Dict | None:
        """
        Даёт прогноз на основании тренда
        :param data: dict
            Словарь с данными о бумаге.
        :return: Dict
            Параметры сделки.
        """
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

        y = np.array(
            average_prices[time.index(list_trend[len(list_trend) - 1][0]) : len(time) - 1]
        )  # Получение значений цен для текущего окна
        x = np.arange(len(y))  # Создание массива индексов
        A = np.vstack([x, np.ones(len(x))]).T  # Построение матрицы для аппроксимации
        slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]  # Линейная аппроксимация

        delta_max = 0.0
        delta_min = 0.0
        last_element_trends = time.index(list_trend[-1][0])
        theory_size = average_prices[last_element_trends]
        for i in range(last_element_trends, len(time)):
            if history[i][3] - theory_size > delta_max:
                delta_max = history[i][3] - theory_size
            if theory_size - history[i][4] > delta_min:
                delta_min = theory_size - history[i][4]
            theory_size += slope

        if average_prices[-1] < theory_size - delta_min * interval_order_in_trend:
            # if average_prices[-1] < theory_size - delta_min * interval_order_in_trend and slope > angle_inclination:
            take_profit = theory_size + delta_max * interval_order_in_trend
            open = history[-1][2]
            close = theory_size - delta_min
            if open <= close:
                close = history[-1][4]
            ticker = data["ticker"]
            id = 1
            if open * (1 + 2 * broker_commission) < take_profit:
                return {"id": id, "ticker": ticker, "open": open, "close": close, "take profit": take_profit}

        return None


async def main() -> None:
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


if __name__ == "__main__":
    asyncio.run(main())
