import pytest_asyncio
from httpx import AsyncClient


# В будущем будет использоваться для тестов
@pytest_asyncio.fixture()
async def async_test_client() -> AsyncClient:
    async with AsyncClient() as client:
        yield client
