from datetime import timedelta

from config import TOKEN
from tinkoff.invest import AsyncClient
from tinkoff.invest.async_services import AsyncServices, CandleInterval


async def get_async_tinkoff_api_client() -> AsyncServices:
    async with AsyncClient(TOKEN) as client:
        yield client


get_tinkoff_client = get_async_tinkoff_api_client()

MAX_INTERVAL_SIZE = {
    CandleInterval.CANDLE_INTERVAL_1_MIN: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_2_MIN: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_3_MIN: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_5_MIN: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_10_MIN: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_15_MIN: timedelta(days=1),
    CandleInterval.CANDLE_INTERVAL_30_MIN: timedelta(days=2),
    CandleInterval.CANDLE_INTERVAL_HOUR: timedelta(days=7),
    CandleInterval.CANDLE_INTERVAL_4_HOUR: timedelta(days=31),
    CandleInterval.CANDLE_INTERVAL_DAY: timedelta(days=366),
    CandleInterval.CANDLE_INTERVAL_WEEK: timedelta(days=732),
    CandleInterval.CANDLE_INTERVAL_MONTH: timedelta(days=3660),
}

ANGLE_INCLINATION = 1 / 20
SIZE_TREND_WINDOW = 10
