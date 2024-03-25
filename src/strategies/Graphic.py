from datetime import datetime, timedelta
from typing import Optional

import matplotlib.pyplot as plt
import Servises
from tinkoff.invest import CandleInterval


class Graphic:
    @staticmethod
    def PrintGraphic(stock_data: dict, indicators: Optional[dict] = None) -> None:
        """
        Отображает график ценовых данных и индикаторов.
        :param stock_data: dict
            Словарь с ценовыми данными, включая историю цен и объемов. Должен содержать ключ "history".
        :param indicators: dict{"color": {"history": history, "alpha": double}}, optional
            Словарь с индикаторами для отображения на графике. Каждый элемент словаря представляет собой
            пару "цвет: данные", где данные включают историю индикатора и прозрачность линии.
        """
        # Извлечение необходимых данных
        history = stock_data["history"][1:]  # пропускаем строку заголовков
        time = [entry[0] for entry in history]
        open_prices = [entry[1] for entry in history]
        close_prices = [entry[2] for entry in history]
        high_prices = [entry[3] for entry in history]
        low_prices = [entry[4] for entry in history]
        volume = [entry[5] for entry in history]

        # Создание графика свечей
        fig, ax1 = plt.subplots()

        # Определение ширины элементов свечи
        width = 0.6
        width2 = 0.05

        # Отображение свечей для положительных и отрицательных дней
        for i in range(len(time)):
            if close_prices[i] >= open_prices[i]:
                plt.bar(time[i], close_prices[i] - open_prices[i], width, bottom=open_prices[i], color="green")
                plt.bar(time[i], high_prices[i] - close_prices[i], width2, bottom=close_prices[i], color="green")
                plt.bar(time[i], low_prices[i] - open_prices[i], width2, bottom=open_prices[i], color="green")
            if close_prices[i] == open_prices[i]:
                plt.bar(time[i], close_prices[i] - open_prices[i], width, bottom=open_prices[i], color="black")
                plt.bar(time[i], high_prices[i] - close_prices[i], width2, bottom=close_prices[i], color="black")
                plt.bar(time[i], low_prices[i] - open_prices[i], width2, bottom=open_prices[i], color="black")
            else:
                plt.bar(time[i], close_prices[i] - open_prices[i], width, bottom=open_prices[i], color="red")
                plt.bar(time[i], high_prices[i] - open_prices[i], width2, bottom=open_prices[i], color="red")
                plt.bar(time[i], low_prices[i] - close_prices[i], width2, bottom=close_prices[i], color="red")

        if indicators:
            for color, data in indicators.items():
                history = data["history"][1:]  # пропускаем строку заголовков
                time = [entry[0] for entry in history]
                values = [entry[1] for entry in history]
                alpha = data.get("alpha", 1.0)  # Значение прозрачности по умолчанию - 1.0 (полностью непрозрачный)
                plt.plot(
                    time, values, color=color, alpha=alpha, label=color
                )  # Построение линии с соответствующим цветом и прозрачностью

        # Отображение объема
        ax2 = ax1.twinx()

        maxClm = max(volume)
        for i in range(len(volume)):
            if i == 0:
                volume[i] = volume[i] / maxClm * 10
            else:
                volume[i] = volume[i] / maxClm

        # Определение цвета объема в зависимости от изменения цены актива
        volume_colors = []
        for i in range(len(volume)):
            if close_prices[i] < open_prices[i]:
                volume_colors.append("red")
            elif close_prices[i] > open_prices[i]:
                volume_colors.append("green")
            else:
                volume_colors.append("black")
        ax2.bar(time, volume, width=0.8, color=volume_colors, alpha=0.5)

        # Добавление сетки
        ax1.grid(True)
        # Поворот подписей оси x
        ax1.set_xticklabels(time, rotation=45, ha="right")

        """
        # Поворот подписей оси x
        ax1.set_xticks(time)
        ax1.set_xticklabels(time, rotation=45, ha='right')
        """

        # Подключение регулирования масштаба колесиком мыши
        ax1.axis("auto")
        # Отображение легенды
        ax1.legend()
        # Отображение графика
        plt.show()


pass


if __name__ == "__main__":
    shares = Servises.Services.GetHistoricCandle(
        Ticker="SBER",
        From=datetime.utcnow() - timedelta(days=400),
        To=datetime.utcnow(),
        Interval=CandleInterval.CANDLE_INTERVAL_DAY,
        IntegerRepresentationTime=False,
    )

    m = [["time", "value"]]
    for i in range(1, len(shares["history"])):
        t = shares["history"][i][0]
        v = (shares["history"][i][1] + shares["history"][i][2]) / 2
        m.append([t, v])

    indicator = {
        "black": {
            "history": m,
            "alpha": 0.5,  # Пример значения прозрачности (от 0 до 1)
        }
    }

    Graphic.PrintGraphic(shares, indicator)
