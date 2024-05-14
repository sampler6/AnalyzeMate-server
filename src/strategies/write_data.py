import asyncio
import json
from datetime import datetime, timedelta, timezone

from tinkoff.invest import CandleInterval

from strategies.base import get_tinkoff_client
from strategies.servises import Services
from strategies.supported_shares import supported_shares


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

    service = Services(client)
    list_shares = list(supported_shares.keys())
    array_data = []
    for i in range(len(list_shares)):
        for j in range(len(list_timeframe)):
            shares = await service.get_historic_candle(
                ticker=list_shares[i],
                from_date=datetime.now(timezone.utc) - time,
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
    asyncio.run(write_data("data_shares.json", timedelta(days=365)))
