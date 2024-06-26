import time
from logging import getLogger
from test.auth.schemas import UserRead

import pytest_asyncio
from config import APP_HOST, APP_PORT
from httpx import AsyncClient

is_init = False
token = ""

logger = getLogger("test")
# Ожидание завершение задач celery на инициализацию
time.sleep(5)


async def init() -> None:
    global token
    assert token == ""
    async with AsyncClient(base_url=f"http://{APP_HOST}:{APP_PORT}/") as test_client:
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


async def get_current_user(client: AsyncClient) -> UserRead:
    response = await client.get("users/me")
    assert response.status_code == 200
    user = UserRead.model_validate(response.json())
    return user


@pytest_asyncio.fixture()
async def client_without_auth() -> AsyncClient:
    async with AsyncClient(base_url=f"http://{APP_HOST}:{APP_PORT}/") as client_without_auth:
        yield client_without_auth
