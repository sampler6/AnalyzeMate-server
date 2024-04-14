import logging

from auth import User
from portfolio.schemas import PortfolioInSchema, PortfolioOutSchema
from repositories.portfolio import PortfolioRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("api")


class PortfolioService:
    def __init__(self, session: AsyncSession):
        self.repository = PortfolioRepository(session)

    async def save_portfolio(self, portfolio: PortfolioInSchema, owner: User) -> PortfolioOutSchema:
        portfolio_db = await self.repository.save_portfolio(portfolio, owner.id)
        return PortfolioOutSchema(id=portfolio_db.id, balance=portfolio_db.balance, owner=portfolio_db.owner)
