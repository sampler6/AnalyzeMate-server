import asyncio
from datetime import datetime, timedelta

import graphic
from servises import Services
from tinkoff.invest import CandleInterval


class Indicators:
    # В процессе написания! Можно не смотреть
    @staticmethod
    def calculate_rsi(data, window):  # type: ignore
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
            result["history"].append([time[i], ema])

        return result


if __name__ == "__main__":
    service = Services()
    shares = asyncio.run(
        service.get_historic_candle(
            ticker="SBER",
            from_date=datetime.utcnow() - timedelta(days=400),
            to_date=datetime.utcnow(),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
            integer_representation_time=False,
        )
    )

    a = Indicators.calculate_rsi(shares, 10)
    indicator = {
        "black": {
            "history": a,
            "alpha": 1,  # Пример значения прозрачности (от 0 до 1)
        }
    }

    graphic.Graphic.print_graphic(shares, indicator)
    print(a)
