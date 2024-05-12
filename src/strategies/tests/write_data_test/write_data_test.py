import asyncio
import json
import os
import time
from datetime import datetime, timezone
from typing import Any

from tinkoff.invest import CandleInterval

from strategies.base import get_tinkoff_client
from strategies.servises import Services
from strategies.supported_shares import supported_shares


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

    client = await anext(get_tinkoff_client)
    list_shares = list(supported_shares.keys())

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

            # TODO: Изменить date в services на datatime
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
    for i in range(len(name_files)):
        with open(f"{interval}\\{name_files[i]}", "r") as f:  # noqa
            array_shares.append(json.load(f))
    with open(f"{interval}.json", "w") as f:  # noqa
        json.dump(array_shares, f)


if __name__ == "__main__":
    # asyncio.run(write_data())
    # print("Конец")

    asyncio.run(rewrite_big_data("CANDLE_INTERVAL_5_MIN"))
