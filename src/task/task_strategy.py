from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Any

from auth.models import UserNotification
from celery import shared_task
from config import LOAD_SECURITIES
from securities.models import HistoricCandles, Securities
from sqlalchemy import and_, select, update
from strategies.prediction import Prediction
from tinkoff.invest.grpc.marketdata_pb2 import CANDLE_INTERVAL_30_MIN

from task.base import sync_session
from task.task_send_notification import send_notification

logger = getLogger("api")


@shared_task(default_retry_delay=2 * 5, max_retries=2)
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

            # отправка уведомлений
            if predict is None:
                continue

            statement = select(UserNotification).where(UserNotification.ticker == security.ticker)
            user_notifications = session.execute(statement).scalars().all()
            user_ids = []

            for user in user_notifications:
                if user.last_commit is not None and (
                    [predict["open"], predict["close"], predict["take profit"]] == [user.open, user.close, user.take]
                    or (datetime.now(timezone.utc) - user.last_commit) < timedelta(hours=1)
                ):
                    continue

                user_ids.append(user.user_id)

            send_notification.delay(
                user_ids,
                f"Уведомление по акции {security.ticker}\n",
                f"Вход: {predict["open"]}\n" f"Стоп: {predict["close"]}\n" f"Тейк: {predict["take profit"]}",
            )
            statement = (
                update(UserNotification)
                .where(and_(UserNotification.ticker == security.ticker, UserNotification.user_id.in_(user_ids)))
                .values(
                    open=predict["open"],
                    close=predict["close"],
                    take=predict["take profit"],
                    last_commit=datetime.now(timezone.utc),
                )
            )
            session.execute(statement)
