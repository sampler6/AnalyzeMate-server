import json
from datetime import datetime

from auth import User
from securities.schemas import HistoricCandlesSchema, SecurityInSchema
from services.historic_candle import HistoricCandlesService
from services.security import SecuritiesService
from tinkoff.invest import CandleInterval

from strategies.supported_shares import supported_shares

with open("strategies/data_shares.json") as f:
    data = json.load(f)["data"]

candle_to_int = {
    "CANDLE_INTERVAL_DAY": CandleInterval.CANDLE_INTERVAL_DAY,
    "CANDLE_INTERVAL_4_HOUR": CandleInterval.CANDLE_INTERVAL_4_HOUR,
    "CANDLE_INTERVAL_HOUR": CandleInterval.CANDLE_INTERVAL_HOUR,
    "CANDLE_INTERVAL_30_MIN": CandleInterval.CANDLE_INTERVAL_30_MIN,
}


async def upload_data_from_files(
    user: User, security_service: SecuritiesService, historic_candle_service: HistoricCandlesService
) -> None:
    """Инициализация свечей из файла data_shares.json в базу данных"""
    # if not user.is_superuser:
    #     raise AccessDeniedException

    global data

    for security in data:
        try:
            # Пытаемся найти акцию по тикеру в бд. Если уже есть - не обрабатываем
            await security_service.get_security_by_ticker(security["ticker"])
            continue
        except Exception:
            # Если ошибка, то значит акции в бд нет и нам надо добавить ее и историю цен
            security_schema = SecurityInSchema(ticker=security["ticker"], name=supported_shares[security["ticker"]])
            await security_service.save_security(security_schema)
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

            await historic_candle_service.save_historic_candles(candles)
