from datetime import timedelta

from tinkoff.invest import CandleInterval

interval_dict = {
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

interval_to_timedelta = {
    CandleInterval.CANDLE_INTERVAL_30_MIN: timedelta(minutes=30),
    CandleInterval.CANDLE_INTERVAL_HOUR: timedelta(hours=1),
    CandleInterval.CANDLE_INTERVAL_4_HOUR: timedelta(hours=4),
    CandleInterval.CANDLE_INTERVAL_DAY: timedelta(days=1),
}
