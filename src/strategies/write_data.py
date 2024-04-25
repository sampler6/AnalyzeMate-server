import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from logging import getLogger

from servises import Services
from supported_shares import supported_shares
from tinkoff.invest import CandleInterval

from strategies.base import get_tinkoff_client

logging.basicConfig()
log = getLogger("tinkoff_client")
log.setLevel(logging.DEBUG)


async def write_data(path: str, time: timedelta) -> None:
    """
    Асинхронно записывает данные в файл.

    :param path: str
        Путь к файлу для записи данных.
    :param time: timedelta
        Временной интервал для получения данных.
    """
    list_timeframe = [
        CandleInterval.CANDLE_INTERVAL_DAY,
        CandleInterval.CANDLE_INTERVAL_4_HOUR,
        CandleInterval.CANDLE_INTERVAL_HOUR,
        CandleInterval.CANDLE_INTERVAL_30_MIN,
    ]

    client = await anext(get_tinkoff_client)

    log.debug("Started to get data")
    service = Services(client)
    array_data = []
    list_shares = [x for x in supported_shares]

    for i in range(len(list_shares)):
        for j in range(len(list_timeframe)):
            log.debug("Request %s data", list_shares[i])
            shares = await service.get_historic_candle(
                ticker=list_shares[i],
                from_date=(datetime.now(timezone.utc) - time),
                to_date=datetime.now(timezone.utc),
                interval=list_timeframe[j],
                integer_representation_time=True,
            )

            array_data.append(shares)

    dict_data = {}
    dict_data["data"] = array_data

    with open(path, "w") as f:  # noqa
        json.dump(dict_data, f)


if __name__ == "__main__":
    asyncio.run(write_data("data_shares.json", timedelta(days=90)))
