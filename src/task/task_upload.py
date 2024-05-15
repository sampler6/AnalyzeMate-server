import asyncio
import json
from datetime import datetime
from logging import getLogger

from celery import shared_task
from securities.models.security import Securities
from services.historic_candle import HistoricCandlesService
from services.security import SecuritiesService
from strategies.supported_shares import supported_shares
from tinkoff.invest import CandleInterval

from task.base import get_strategies_historic_candles_service, get_strategies_securities_service

logger = getLogger("api")


@shared_task(default_retry_delay=2 * 5, max_retries=2)
def upload_data_from_files(**kwargs) -> None:  # type:ignore
    """Инициализация свечей из файла data_shares.json в базу данных"""
    logger.info("Начата процедура записи предзагруженных акций в базу данных")

    with open("strategies/data_shares.json") as f:
        data = json.load(f)["data"]

    security_service: SecuritiesService = asyncio.run(anext(get_strategies_securities_service))  # type:ignore
    historic_candle_service: HistoricCandlesService = asyncio.run(anext(get_strategies_historic_candles_service))  # type:ignore

    # Получение существующих данных из бд:
    (existing_tickers_in_db, existing_candles_in_db) = get_existing_securities_and_historic_candles_from_db(
        security_service, historic_candle_service
    )

    candles_to_append, securities_to_append = process_new_data(data, existing_tickers_in_db, existing_candles_in_db)

    st = datetime.now()
    if securities_to_append:
        asyncio.run(security_service.repository.save_all(securities_to_append))
        asyncio.run(security_service.repository.session.commit())
    if candles_to_append:
        asyncio.run(historic_candle_service.insert_bulk(candles_to_append))
    result_time = datetime.now() - st
    logger.info("Данные загружены в бд за %sms", result_time.seconds * 1000 + result_time.microseconds / 1000)


def get_existing_securities_and_historic_candles_from_db(
    security_service: SecuritiesService, historic_candle_service: HistoricCandlesService
) -> tuple[list[str], dict[tuple[str, int], set[float]]]:
    st = datetime.now()
    existing_tickers_in_db = [security.ticker for security in asyncio.run(security_service.get_all_securities())]
    # Словарь с ключом (ticker, timeframe) и значением хэш сет из меток времени свечей из бд
    existing_candles_in_db: dict[tuple[str, int], set[float]] = asyncio.run(
        historic_candle_service.get_existing_timestamp_for_all_tickers()
    )

    result_time = datetime.now() - st
    logger.info("Данные из базы данных получены за %sms", result_time.seconds * 1000 + result_time.microseconds / 1000)
    return existing_tickers_in_db, existing_candles_in_db


def process_new_data(
    data: list[dict], existing_tickers_in_db: list[str], existing_candles_in_db: dict[tuple[str, int], set[float]]
) -> tuple[list[dict], list[Securities]]:
    st = datetime.now()

    candle_to_int = {
        "CANDLE_INTERVAL_DAY": CandleInterval.CANDLE_INTERVAL_DAY,
        "CANDLE_INTERVAL_4_HOUR": CandleInterval.CANDLE_INTERVAL_4_HOUR,
        "CANDLE_INTERVAL_HOUR": CandleInterval.CANDLE_INTERVAL_HOUR,
        "CANDLE_INTERVAL_30_MIN": CandleInterval.CANDLE_INTERVAL_30_MIN,
    }

    candles_to_append: list[dict] = []
    security_to_append: list[Securities] = []
    for security in data:
        if security["ticker"] not in existing_tickers_in_db:
            # Если тикера нет, добавляем
            security_to_append.append(
                Securities(
                    ticker=security["ticker"],
                    name=supported_shares[security["ticker"]],
                    price=round(security["history"][len(security["history"]) - 1][2], 2),
                )
            )
            existing_tickers_in_db.append(security["ticker"])

        for candle in security["history"][1:]:
            if candle[0] not in existing_candles_in_db[(security["ticker"], candle_to_int[security["timeframe"]])]:
                candles_to_append.append(
                    {
                        "ticker": security["ticker"],
                        "open": candle[1],
                        "close": candle[2],
                        "highest": candle[3],
                        "lowest": candle[4],
                        "volume": candle[5],
                        "timeframe": candle_to_int[security["timeframe"]],
                        "timestamp": candle[0],
                    }
                )
    result_time = datetime.now() - st
    logger.info("Данные с файла обработаны за %sms", result_time.seconds * 1000 + result_time.microseconds / 1000)

    return candles_to_append, security_to_append
