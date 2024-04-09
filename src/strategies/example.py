import asyncio

from securities.schemas import HistoricCandlesSchema, SecurityInSchema
from tinkoff.invest import CandleInterval

from strategies.base import get_historic_candle_repository, get_securities_repository


async def main() -> None:
    # записываем данные либо в словарик, либо через аргументы класса(пример у свечей)
    share = {"ticker": "SBER", "name": "Сбербанк"}

    # создаем репозиторий
    sec_repo = await anext(get_securities_repository)
    # создаем схему
    share_schema = SecurityInSchema(**share)
    # вывод для примера
    print(share_schema)
    # сохраняем в бд
    await sec_repo.save_security(share_schema)

    # Проверка на существование акции по тикеру
    if await sec_repo.get_security_by_ticker(ticker="SBER") is None:
        # Акции нет
        return

    # Аналогичное создание схемы, но через аргументы. Если тикер не будет существовать в бд во время сохранение
    # - exception
    hist = HistoricCandlesSchema(
        open=13.4,
        close=143.3,
        highest=1,
        lowest=3,
        volume=3,
        ticker="SBER",
        timeframe=CandleInterval.CANDLE_INTERVAL_HOUR,
    )
    print(hist.model_dump())
    d = {
        "open": 13.4,
        "close": 143.3,
        "highest": 1,
        "lowest": 3,
        "volume": 3,
        "ticker": "SBER",
        "timeframe": CandleInterval.CANDLE_INTERVAL_HOUR,
    }
    hist2 = HistoricCandlesSchema(**d)
    print(hist2.model_dump())
    hist_repo = await anext(get_historic_candle_repository)
    # сохранение одной свечи
    await hist_repo.save_historic_candle(hist2)
    # сохранения массива свеч
    await hist_repo.save_historic_candles([hist, hist2])


if __name__ == "__main__":
    asyncio.run(main())
