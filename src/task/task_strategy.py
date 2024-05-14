from datetime import datetime
from logging import getLogger
from typing import Any

from config import LOAD_SECURITIES
from securities.models import HistoricCandles, Securities
from sqlalchemy import and_, select
from strategies.prediction import Prediction
from tinkoff.invest.grpc.marketdata_pb2 import CANDLE_INTERVAL_30_MIN

from task.base import sync_session
from task.task import app_celery

logger = getLogger("api")


@app_celery.task(default_retry_delay=2 * 5, max_retries=2)
def start_strategy() -> None:
    if not LOAD_SECURITIES:
        return
    with sync_session() as session:
        securities = session.execute(select(Securities)).scalars().all()

        for security in securities:
            data: dict[str, Any] = {
                "figi": "BBG004RVFFC0",
                "ticker": security.ticker,
                "timeframe": CANDLE_INTERVAL_30_MIN,
                "history": [["time", "open", "close", "high", "low", "volume"]],
            }

            candles_db = (
                session.execute(
                    select(HistoricCandles)
                    .where(and_(HistoricCandles.ticker == security.ticker, HistoricCandles.timeframe == 9))
                    .order_by(HistoricCandles.timestamp)
                )
                .scalars()
                .all()
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
