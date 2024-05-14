import asyncio
import json
import os
import time
from datetime import datetime, timezone
from typing import Any

import pytz  # type: ignore
from tinkoff.invest import CandleInterval

from strategies.base import get_tinkoff_client
from strategies.servises import Services


async def write_data() -> None:
    """
    Асинхронно записывает данные в файл.

    :param path: str
        Путь к файлу для записи данных.
    :param time: timedelta
        Временной интервал для получения данных.
    """
    start_time = time.time()

    list_timeframe = [
        CandleInterval.CANDLE_INTERVAL_DAY,
        CandleInterval.CANDLE_INTERVAL_4_HOUR,
        CandleInterval.CANDLE_INTERVAL_HOUR,
        CandleInterval.CANDLE_INTERVAL_30_MIN,
        CandleInterval.CANDLE_INTERVAL_15_MIN,
        CandleInterval.CANDLE_INTERVAL_5_MIN,
    ]

    list_shares = [
        "TATN",
        "ROSN",
        "LKOH",
        "GAZP",
        "SIBN",
        "PIKK",
        "SMLT",
        "MAGN",
        "NLMK",
        "CHMF",
        "SBER",
        "VTBR",
        "TCSG",
        "AQUA",
        "ABIO",
        "MDMG",
        "CBOM",
        "ALRS",
        "LENT",
        "VKCO",
        "RUAL",
        "AFKS",
        "AFLT",
        "EUTR",
        "IRAO",
        "POSI",
        "BELU",
        "PHOR",
        "PLZL",
        "RTKMP",
    ]

    client = await anext(get_tinkoff_client)

    service = Services(client)
    for i in range(len(list_timeframe)):
        for j in range(len(list_shares)):
            share = {}
            response = await service.get_shares(list_shares[j])
            share["ticker"] = response.ticker
            share["first_1min_candle_date"] = str(response.first_1min_candle_date)
            share["name"] = response.name
            share["lot"] = response.lot
            share["min_price_increment"] = str(_cast_money(response.min_price_increment))
            share["sector"] = response.sector
            share["currency"] = response.currency
            share["figi"] = response.figi
            share["timeframe"] = str(list_timeframe[i].name)
            share["history"] = await service.get_historic_candle(
                ticker=list_shares[j],
                from_date=response.first_1min_candle_date,
                to_date=datetime.now(timezone.utc),
                interval=list_timeframe[i],
                integer_representation_time=False,
            )

            with open(f"{str(list_timeframe[i].name)}\\{list_shares[j]}", "w") as f:  # noqa
                json.dump(share, f)
            print(f"{str(list_timeframe[i].name)}    {list_shares[j]}")

            elapsed_time = time.time() - start_time
            print(str(elapsed_time))


def _cast_money(v: Any) -> float:
    return v.units + v.nano / 1e9


async def rewrite_big_data(interval: str) -> None:
    name_files = os.listdir(interval)
    array_shares = []

    # Часть для сплошной перезаписи
    # for i in range(len(name_files)):
    #     with open(f"{interval}\\{name_files[i]}", "r") as f:  # noqa
    #         array_shares.append(json.load(f))
    # with open(f"{interval}.json", "w") as f:  # noqa
    #     json.dump(array_shares, f)

    # Перезапись с 01.06.22
    for i in range(len(name_files)):
        with open(f"{interval}\\{name_files[i]}", "r") as f:  # noqa
            data = json.load(f)
            history = data["history"]["history"]
            short_history = [history[0]]
            for i in range(1, len(history)):
                # datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S%z")
                if datetime.strptime(history[i][0], "%Y-%m-%d %H:%M:%S%z") > datetime(
                    year=2022, month=6, day=1, hour=0, minute=0, second=0, tzinfo=pytz.UTC
                ):
                    short_history.append(history[i])
            data["history"]["history"] = short_history
            array_shares.append(data)
    with open(f"{interval}_2022.json", "w") as f:  # noqa
        json.dump(array_shares, f)


if __name__ == "__main__":
    # asyncio.run(write_data())
    # print("Конец")

    list_timeframe = [
        CandleInterval.CANDLE_INTERVAL_DAY,
        CandleInterval.CANDLE_INTERVAL_4_HOUR,
        CandleInterval.CANDLE_INTERVAL_HOUR,
        CandleInterval.CANDLE_INTERVAL_30_MIN,
        CandleInterval.CANDLE_INTERVAL_15_MIN,
        # CandleInterval.CANDLE_INTERVAL_5_MIN,
    ]
    for i in range(len(list_timeframe)):
        asyncio.run(rewrite_big_data(str(list_timeframe[i].name)))
