from logging import getLogger
from typing import Iterable, Optional

from db.base_repository import BaseRepository
from securities.models import Securities
from securities.schemas import SecurityInSchema
from sqlalchemy import func, or_, select, text

logger = getLogger("api")


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

    async def search_security(self, search: str) -> list[str]:
        """
        Поиск по совпадению триграмм. Необходим плагин pg_trgm в postgresql.
        Возвращает список тикеров.
        """

        # Установка мягкого лимита совпадения для поиска
        await self.session.execute(text("SELECT set_limit(0.01);"))

        statement = select(
            Securities.ticker, func.similarity(Securities.ticker, search), func.similarity(Securities.name, search)
        ).where(
            or_(Securities.ticker.bool_op("%")(search), Securities.name.bool_op("%")(search)),
        )

        result = (await self.session.execute(statement)).all()

        # Считаем значение максимального совпадения и делим пополам. Акции, которые ниже этого числа, не выдаем
        tickers = []
        medium = max([max(x[1], x[2]) for x in result])

        for ticker in sorted(result, key=lambda x: max(x[1], x[2]), reverse=True):
            if max(ticker[1], ticker[2]) >= 0.5 * medium:
                tickers.append(ticker[0])

        return tickers
