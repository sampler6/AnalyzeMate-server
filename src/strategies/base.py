from typing import AsyncGenerator

from config import TOKEN
from tinkoff.invest import AsyncClient
from tinkoff.invest.async_services import AsyncServices


async def get_async_tinkoff_api_client() -> AsyncGenerator[AsyncServices, None]:
    async with AsyncClient(TOKEN) as client:
        yield client
