import asyncio
import json
from datetime import datetime, timedelta, timezone

from list_shares import list_shares
from tinkoff.invest import CandleInterval

from strategies.base import get_historic_candle_repository, get_securities_repository, get_tinkoff_client
from strategies.servises import Services


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
    securities_repository = await anext(get_securities_repository)
    historic_candles_repository = await anext(get_historic_candle_repository)

    service = Services(client, securities_repository, historic_candles_repository)
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
