import asyncio
from datetime import datetime, timezone
from typing import Any

import pytz  # type: ignore
from celery import shared_task
from securities.models.historic_candles import HistoricCandles
from securities.models.security import Securities
from services.historic_candle import HistoricCandlesService
from services.security import SecuritiesService
from sqlalchemy import desc, select, update
from strategies.base import get_tinkoff_client
from strategies.servises import Services
from strategies.supported_shares import supported_shares
from tinkoff.invest import CandleInterval

from task.base import get_strategies_historic_candles_service, get_strategies_securities_service, sync_session


@shared_task(default_retry_delay=2 * 5, max_retries=2)
def get_new_candles(**kwargs) -> None:  # type:ignore
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_get_new_candles())
    loop.close()


async def _get_new_candles() -> None:  # type:ignore
    """Получение новых свечей"""
    data = await get_data_from_tinkoff()

    security_service: SecuritiesService = await anext(get_strategies_securities_service)  # type:ignore
    historic_candle_service: HistoricCandlesService = await anext(get_strategies_historic_candles_service)  # type:ignore

    # Получение существующих данных из бд:
    (existing_tickers_in_db, existing_candles_in_db) = await get_existing_securities_and_historic_candles_from_db(
        security_service, historic_candle_service
    )

    candles_to_append, securities_to_append = await process_new_data(
        data, existing_tickers_in_db, existing_candles_in_db
    )

    if securities_to_append:
        await security_service.repository.save_all(securities_to_append)
        await security_service.repository.session.commit()
    if candles_to_append:
        await historic_candle_service.insert_bulk(candles_to_append)

    await historic_candle_service.repository.session.commit()
    await security_service.repository.session.commit()


async def get_data_from_tinkoff() -> list[Any]:
    list_timeframe = [
        CandleInterval.CANDLE_INTERVAL_DAY,
        CandleInterval.CANDLE_INTERVAL_4_HOUR,
        CandleInterval.CANDLE_INTERVAL_HOUR,
        CandleInterval.CANDLE_INTERVAL_30_MIN,
    ]

    client = await anext(get_tinkoff_client)

    service = Services(client)
    with sync_session() as session:
        time = datetime.fromtimestamp(
            session.execute(select(HistoricCandles.timestamp).order_by(desc(HistoricCandles.timestamp)).limit(1))
            .scalars()
            .one()
            / 1000
        )
        time = pytz.UTC.localize(time)

        list_shares = session.execute(select(Securities.ticker)).scalars().all()

    array_data = []
    for i in range(len(list_shares)):
        for j in range(len(list_timeframe)):
            shares = await service.get_historic_candle(
                ticker=list_shares[i],
                from_date=time,
                to_date=datetime.now(timezone.utc),
                interval=list_timeframe[j],
                integer_representation_time=True,
            )

            array_data.append(shares)

    return array_data


async def get_existing_securities_and_historic_candles_from_db(
    security_service: SecuritiesService, historic_candle_service: HistoricCandlesService
) -> tuple[list[str], dict[tuple[str, int], set[float]]]:
    existing_tickers_in_db = [security.ticker for security in await security_service.get_all_securities()]
    # Словарь с ключом (ticker, timeframe) и значением хэш сет из меток времени свечей из бд
    existing_candles_in_db: dict[
        tuple[str, int], set[float]
    ] = await historic_candle_service.get_existing_timestamp_for_all_tickers()

    return existing_tickers_in_db, existing_candles_in_db


async def process_new_data(
    data: list[dict], existing_tickers_in_db: list[str], existing_candles_in_db: dict[tuple[str, int], set[float]]
) -> tuple[list[dict], list[Securities]]:
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
            if len(security["history"]) != 1:
                # Если тикера нет, добавляем
                security_to_append.append(
                    Securities(
                        ticker=security["ticker"],
                        name=supported_shares[security["ticker"]],
                        price=round(security["history"][len(security["history"]) - 1][2], 2),
                    )
                )
                existing_tickers_in_db.append(security["ticker"])
        else:
            if len(security["history"]) != 1:
                stmt = (
                    update(Securities)
                    .where(Securities.ticker == security["ticker"])
                    .values(price=round(security["history"][len(security["history"]) - 1][2], 2))
                )
                with sync_session() as session:
                    session.execute(stmt)
                    session.commit()

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

    return candles_to_append, security_to_append
