from logging import getLogger

import pytest_asyncio
from config import APP_HOST, APP_PORT
from httpx import AsyncClient

is_init = False
token = ""

logger = getLogger("test")


async def init() -> None:
    global token
    assert token == ""
    data = {
        "email": "test@example.com",
        "password": "Test12345",
        "birthdate": "2024-04-06T16:09:20.161173Z",
        "patronymic": "test",
        "surname": "client",
        "name": "aaa",
        "balance": 0,
        "config": {"test": "test"},
    }
    async with AsyncClient(base_url=f"http://{APP_HOST}:{APP_PORT}/") as test_client:
        response = await test_client.post("auth/register", json=data)
        assert response.status_code not in ["200", "400"], "Cannot register test_user"
        response = await test_client.post("auth/login", data={"username": "test@example.com", "password": "Test12345"})
        assert response.status_code == 200
        token = response.json()["access_token"]


@pytest_asyncio.fixture()
async def client() -> AsyncClient:
    global is_init, token
    if not is_init:
        await init()
        is_init = True
    async with AsyncClient(
        base_url=f"http://{APP_HOST}:{APP_PORT}/", headers={"Authorization": f"Bearer {token}"}
    ) as client:
        yield client


@pytest_asyncio.fixture()
async def client_without_auth() -> AsyncClient:
    async with AsyncClient(base_url=f"http://{APP_HOST}:{APP_PORT}/") as client_without_auth:
        yield client_without_auth
