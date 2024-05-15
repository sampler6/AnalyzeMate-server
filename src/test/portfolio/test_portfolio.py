from test.conftest import get_current_user
from test.settings_test import check_time

import pytest
from faker import Faker
from httpx import AsyncClient
from portfolio.schemas import PortfolioOutSchema


@pytest.mark.parametrize(
    "balance, status_code",
    [
        (1000, 200),
        ("Vasya", 422),
    ],
)
async def test_create_portfolio(
    balance: str,
    status_code: int,
    client: AsyncClient,
) -> None:
    response = await client.post(
        "portfolio/",
        json={"balance": balance},
    )

    assert response.status_code == status_code
    if status_code == 200:
        data = response.json()
        portfolio = PortfolioOutSchema.model_validate(data)

        response = await client.delete(f"portfolio/{portfolio.id}/")
        assert response.status_code == 200


@check_time(2100)
async def test_portfolios_functionality(client: AsyncClient) -> None:
    """
    Комплексный тест на проверку работы с портфелем.
    Включает в себя:
    Создание 3 портфелей с балансом, получение портфелей текущего пользователя,
    проверку соответствия баланса пользователя и суммы балансов портфелей,
    невозможность создать 4 портфель, удаление созданных портфелей, проверку изменения баланса после удаления

    Запросы:
    4 запроса на создание портфелей
    1 запрос на получение портфелей пользователя
    3 запроса на удаление
    2 запроса на получение текущего пользователя
    2100мс
    """
    faker = Faker()
    balances = [faker.random.randint(0, 1000), faker.random.randint(0, 1000), faker.random.randint(0, 1000)]
    for balance in balances:
        response = await client.post(
            "portfolio/",
            json={"balance": balance},
        )
        assert response.status_code == 200

    response = await client.get("portfolio/", params={"include_securities": "false"})

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    portfolios = []
    current_user = await get_current_user(client)

    for portfolio in data:
        portfolio_schema = PortfolioOutSchema.model_validate(portfolio)
        assert portfolio_schema.owner == current_user.id
        portfolios.append(portfolio_schema)

    assert len(portfolios) == 3
    assert sum(map(lambda x: x.balance, portfolios)) == current_user.balance

    response = await client.post(
        "portfolio/",
        json={"balance": 23},
    )
    assert response.status_code == 409

    for portfolio in portfolios:
        response = await client.delete(f"portfolio/{portfolio.id}/")
        assert response.status_code == 200

    current_user = await get_current_user(client)
    assert current_user.balance == 0
