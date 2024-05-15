from test.securities.schemas import (
    HistoricCandlesOutSchema,
    SecurityOutSchema,
    SecurityShortOutSchema,
    supported_shares,
)
from test.settings_test import check_time

import pytest
from faker import Faker
from httpx import AsyncClient

"""
Во всех тестах используются
данные предзагруженных акций
за неделю с 8.05 по 15.05 23:00 по МСК.
"""


@check_time(300)
async def test_get_all_securities(client: AsyncClient) -> None:
    """
    Тестирование выдачи всех акций
    """
    response = await client.get("/securities/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 30
    for security in data:
        SecurityShortOutSchema.model_validate(security)


def get_random_list_of_supported_shares(num: int) -> list[str]:
    faker = Faker()
    start = faker.random.randint(0, 15)

    return list(supported_shares.keys())[start : start + num]


@pytest.mark.parametrize(
    ("num_of_shares", "timeframe"),
    [
        (1, 4),
        (5, 9),
        (5, 5),
        (5, 11),
        (5, 4),
        (10, 9),  # Стресс тест
    ],
)
@check_time(1500)
async def test_get_securities_by_ticker(num_of_shares: int, timeframe: int, client: AsyncClient) -> None:
    """
    Тестирование выдачи акций по массиву тикеров с выдачей свечей с таймфреймом 30 минут
    """
    params = {"include_historic_candles": "true", "timeframe": int(timeframe)}
    tickers = get_random_list_of_supported_shares(num_of_shares)

    response = await client.post("securities/", json=tickers, params=params)

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(tickers)
    response_tickers = []
    for security in data:
        security_schema = SecurityOutSchema.model_validate(security)
        response_tickers.append(security_schema.ticker)

        candles = security_schema.historic_candles
        assert isinstance(candles, list)
        assert len(candles) > 0
        for candle in candles:
            candle_schema = HistoricCandlesOutSchema.model_validate(candle)
            assert candle_schema.timeframe == timeframe

    assert response_tickers == sorted(tickers)


@pytest.mark.parametrize(
    ("search", "full_ticker_or_name", "max_length"),
    [
        ("SBER", "SBER", 1),
        ("Сбер", "Сбер Банк", 1),
        ("Газ", "Газпром нефть", 2),
        ("GAZ", "GAZP", 1),
    ],
)
@check_time(300)
async def test_search_security(search: str, full_ticker_or_name: str, max_length: int, client: AsyncClient) -> None:
    """
    Тестирование поиска акций по тикеру или названию
    search - строка поиска
    full_ticker_or_name - тикер или имя искомой акции
    max_length - максимальное число акций в ответе
    """
    response = await client.get(f"securities/search/{search}")

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= max_length
    response_tickers = []
    response_names = []
    for security in data:
        security_schema = SecurityShortOutSchema.model_validate(security)
        response_tickers.append(security_schema.ticker)
        response_names.append(security_schema.name)

    assert full_ticker_or_name in response_tickers or full_ticker_or_name in response_names
