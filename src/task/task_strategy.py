import asyncio
from datetime import datetime
from logging import getLogger
from typing import Any

from services.historic_candle import HistoricCandlesService
from services.security import SecuritiesService
from strategies.prediction import Prediction
from tinkoff.invest.grpc.marketdata_pb2 import CANDLE_INTERVAL_30_MIN

from task.base import get_strategies_historic_candles_service, get_strategies_securities_service
from task.task import app_celery

logger = getLogger("api")


@app_celery.task(default_retry_delay=2 * 5, max_retries=2)
def start_strategy() -> None:
    security_service: SecuritiesService = asyncio.run(anext(get_strategies_securities_service))  # type: ignore
    historic_candle_service: HistoricCandlesService = asyncio.run(anext(get_strategies_historic_candles_service))  # type: ignore

    securities = asyncio.run(security_service.get_all_securities())

    for security in securities:
        data: dict[str, Any] = {
            "figi": "BBG004RVFFC0",
            "ticker": security.ticker,
            "timeframe": CANDLE_INTERVAL_30_MIN,
            "history": [["time", "open", "close", "high", "low", "volume"]],
        }
        candles_db = sorted(
            asyncio.run(historic_candle_service.get_historic_candles_by_ticker_and_timeframe(security.ticker, 9)),
            key=lambda x: x.timestamp,
        )

        for candle in candles_db:
            data["history"].append(
                [
                    datetime.fromtimestamp(candle.timestamp / 1000),
                    candle.open,
                    candle.close,
                    candle.highest,
                    candle.lowest,
                    candle.volume,
                ]
            )

        predict = Prediction.get_RSI_predict(data)  # type: ignore
        logger.info(predict)
