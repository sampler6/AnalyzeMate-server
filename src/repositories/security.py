from typing import Iterable, Optional

from db.base_repository import BaseRepository
from securities.models import Securities
from sqlalchemy import select


class SecuritiesRepository(BaseRepository):
    async def get_security_by_ticker(self, ticker: str) -> Optional[Securities]:
        statement = select(Securities).where(Securities.ticker == ticker)
        return await self.one_or_none(statement)

    async def get_securities_by_tickers(self, tickers: list[str]) -> Iterable[Securities]:
        statement = select(Securities).filter(Securities.ticker.in_(tickers))
        return await self.all(statement)

    async def get_all_securities(self) -> Iterable[Securities]:
        statement = select(Securities)
        return await self.all(statement)
