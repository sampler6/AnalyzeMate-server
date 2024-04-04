from typing import AsyncGenerator

from config import TOKEN
from tinkoff.invest import AsyncClient
from tinkoff.invest.async_services import AsyncServices


async def get_async_tinkoff_api_client() -> AsyncGenerator[AsyncServices, None]:
    if TOKEN is None:
        raise Exception("invalid tinkoff token")
    async with AsyncClient(TOKEN) as client:
        yield client


get_tinkoff_client = get_async_tinkoff_api_client()
