from datetime import datetime, timedelta
from tinkoff.invest import CandleInterval
import Servises
import Graphic

class Indicators:
    @staticmethod
    def CalculateRSI(data, window):
        history = data['history'][1:]  # пропускаем строку заголовков
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
            "history": [["time", "value"]]
        }

        # Вычисление EMA для остальных точек
        for i in range(window, len(close_prices)):
            ema = (close_prices[i] - ema_values[-1]) * alpha + ema_values[-1]
            ema_values.append(ema)
            result["history"].append([time[i], ema])

        return result


if __name__ == "__main__":
    shares = Servises.Services.GetHistoricCandle(Ticker="SBER", From=datetime.utcnow() - timedelta(days=400),
                                                 To=datetime.utcnow(), Interval=CandleInterval.CANDLE_INTERVAL_DAY,
                                                 IntegerRepresentationTime=False)

    a = Indicators.CalculateRSI(shares, 10)
    indicator = {
        "black":
            {
                "history": a,
                "alpha": 1  # Пример значения прозрачности (от 0 до 1)
            }
    }

    Graphic.Graphic.PrintGraphic(shares, indicator)
    print(a)