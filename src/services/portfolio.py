import logging

from auth import User
from exceptions.base import AccessDeniedException
from exceptions.portfolio import PortfolioNotFoundError
from portfolio.schemas import PortfolioBalanceSchema, PortfolioInSchema, PortfolioOutSchema
from repositories.portfolio import PortfolioRepository
from repositories.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("api")


class PortfolioService:
    def __init__(self, session: AsyncSession):
        self.repository = PortfolioRepository(session)
        self.user_repository = UserRepository(session)

    async def save_portfolio(self, portfolio: PortfolioInSchema, owner: User) -> PortfolioOutSchema:
        portfolio_db = await self.repository.save_portfolio(portfolio, owner.id)
        return PortfolioOutSchema(id=portfolio_db.id, balance=portfolio_db.balance, owner=portfolio_db.owner)

    async def get_portfolio_by_id(
        self, portfolio_id: int, user_id: int, include_securities: bool
    ) -> PortfolioOutSchema:
        portfolio = await self.repository.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            raise PortfolioNotFoundError(id=portfolio_id)
        if portfolio.owner != user_id:
            raise AccessDeniedException("You're not the owner of portfolio")

        return PortfolioOutSchema(id=portfolio.id, balance=portfolio.balance, owner=portfolio.owner)

    async def get_portfolios_by_owner_id(self, owner_id: int, include_securities: bool) -> list[PortfolioOutSchema]:
        result = [
            PortfolioOutSchema(
                id=portfolio.id,
                balance=portfolio.balance,
                owner=portfolio.owner,
            )
            for portfolio in await self.repository.get_portfolios_by_owner_id(owner_id=owner_id)
        ]
        return result

    async def delete_portfolio_by_id(self, portfolio_id: int, user_id: int) -> None:
        owner = await self.repository.get_portfolio_owner_by_portfolio_id(portfolio_id)
        if owner is None:
            raise PortfolioNotFoundError(id=portfolio_id)
        if owner != user_id:
            raise AccessDeniedException("You're not the owner of portfolio")

        await self.repository.delete_portfolio_by_id(portfolio_id)

    async def update_portfolio_balance(
        self, portfolio_id: int, new_balance: float, user_id: int
    ) -> PortfolioBalanceSchema:
        portfolio = await self.repository.get_portfolio_by_id(portfolio_id)
        if portfolio is None:
            raise PortfolioNotFoundError(id=portfolio_id)
        if portfolio.owner != user_id:
            raise AccessDeniedException("You're not the owner of portfolio")

        new_user_balance = await self.user_repository.add_delta_to_user_balance(
            user_id=user_id, delta=new_balance - portfolio.balance
        )
        new_portfolio_balance = await self.repository.update_portfolio_balance(portfolio=portfolio, balance=new_balance)

        return PortfolioBalanceSchema(portfolio_balance=new_portfolio_balance, user_balance=new_user_balance)
