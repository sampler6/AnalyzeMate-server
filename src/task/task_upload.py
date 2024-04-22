import asyncio
import json
from datetime import datetime
from logging import getLogger

from celery import shared_task
from securities.schemas import HistoricCandlesSchema, SecurityInSchema
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

    candle_to_int = {
        "CANDLE_INTERVAL_DAY": CandleInterval.CANDLE_INTERVAL_DAY,
        "CANDLE_INTERVAL_4_HOUR": CandleInterval.CANDLE_INTERVAL_4_HOUR,
        "CANDLE_INTERVAL_HOUR": CandleInterval.CANDLE_INTERVAL_HOUR,
        "CANDLE_INTERVAL_30_MIN": CandleInterval.CANDLE_INTERVAL_30_MIN,
    }

    for security in data:
        try:
            # Пытаемся найти акцию по тикеру в бд. Если уже есть - не обрабатываем
            asyncio.run(security_service.get_security_by_ticker(security["ticker"]))
            continue
        except Exception:
            # Если ошибка, то значит акции в бд нет и нам надо добавить ее и историю цен
            security_schema = SecurityInSchema(ticker=security["ticker"], name=supported_shares[security["ticker"]])
            asyncio.run(security_service.save_security(security_schema))
            candles: list[HistoricCandlesSchema] = []
            for candle in security["history"][1:]:
                candles.append(
                    HistoricCandlesSchema(
                        ticker=security["ticker"],
                        open=candle[1],
                        close=candle[2],
                        highest=candle[3],
                        lowest=candle[4],
                        volume=candle[5],
                        timeframe=candle_to_int[security["timeframe"]],
                        timestamp=datetime.fromtimestamp(candle[0] / 1000),
                    )
                )

            asyncio.run(historic_candle_service.save_historic_candles(candles))

    logger.info("Акции загружены успешно")
