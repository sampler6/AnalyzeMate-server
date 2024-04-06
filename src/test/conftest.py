import pytest_asyncio
from config import APP_HOST, APP_PORT
from httpx import AsyncClient


@pytest_asyncio.fixture()
async def test_client() -> AsyncClient:
    async with AsyncClient(base_url=f"http://{APP_HOST}:{APP_PORT}/") as client:
        yield client
