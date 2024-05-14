import pytest
from httpx import AsyncClient


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
        "/portfolio/",
        json={"balance": balance},
    )

    assert response.status_code == status_code
