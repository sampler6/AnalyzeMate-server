from typing import Iterable, Optional

from db.base_repository import BaseRepository
from securities.models import Securities
from securities.schemas import SecurityInSchema
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

    async def save_security(self, security: SecurityInSchema) -> None:
        await self.save(Securities(**security.model_dump()))
        await self.session.commit()

    async def save_securities(self, securities: list[SecurityInSchema]) -> None:
        securities_db: list[Securities] = list()
        for security in securities:
            securities_db.append(Securities(**security.model_dump()))

        await self.save_all(securities)
        await self.session.commit()
