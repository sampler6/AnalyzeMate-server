from typing import Iterable

from db.base_repository import BaseRepository
from portfolio.models import Portfolio
from portfolio.schemas import PortfolioInSchema
from sqlalchemy import delete, select


class PortfolioRepository(BaseRepository):
    async def save_portfolio(self, portfolio: PortfolioInSchema, owner: int) -> Portfolio:
        result = await self.save(Portfolio(**portfolio.model_dump() | {"owner": owner}))
        return result

    async def get_portfolio_by_id(self, portfolio_id: int) -> Portfolio | None:
        statement = select(Portfolio).where(Portfolio.id == portfolio_id)
        return await self.one_or_none(statement)

    async def get_portfolios_ids_by_owner_id(self, owner_id: int) -> Iterable[int]:
        statement = select(Portfolio.id).where(Portfolio.owner == owner_id).order_by(Portfolio.id)
        return await self.all(statement)

    async def delete_portfolio_by_id(self, portfolio_id: int) -> None:
        query = delete(Portfolio).where(Portfolio.id == portfolio_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_portfolio_owner_by_portfolio_id(self, portfolio_id: int) -> int | None:
        query = select(Portfolio.owner).where(Portfolio.id == portfolio_id)
        result = await self.session.execute(query)
        return result.one_or_none()

    async def update_portfolio_balance(self, portfolio: Portfolio, balance: float) -> float:
        portfolio.balance = balance
        portfolio = await self.save(portfolio)
        return portfolio.balance
