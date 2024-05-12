import logging

from auth import User
from exceptions.base import AccessDeniedException, ConflictingStateException, ValidationException
from exceptions.portfolio import PortfolioNotFoundError
from portfolio.schemas import PortfolioBalanceSchema, PortfolioInSchema, PortfolioOutSchema
from repositories.portfolio import PortfolioRepository
from repositories.security import SecuritiesRepository
from repositories.transaction import TransactionsRepository
from repositories.user import UserRepository
from securities.schemas import SecurityWithVolumeAndPriceOutSchema
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("api")


class PortfolioService:
    def __init__(self, session: AsyncSession):
        self.repository = PortfolioRepository(session)
        self.user_repository = UserRepository(session)
        self.transaction_repository = TransactionsRepository(session)
        self.securities_repository = SecuritiesRepository(session)

    async def save_portfolio(self, portfolio: PortfolioInSchema, owner: User) -> PortfolioOutSchema:
        user_portfolios = [x for x in await self.repository.get_portfolios_ids_by_owner_id(owner.id)]
        if len(user_portfolios) > 2:
            raise ConflictingStateException("User couldn't have more 3 portfolios")

        portfolio_db = await self.repository.save_portfolio(portfolio, owner.id)

        if portfolio.balance > 0:
            await self.user_repository.add_delta_to_user_balance(user_id=owner.id, delta=portfolio.balance)

        return PortfolioOutSchema(
            id=portfolio_db.id, balance=portfolio_db.balance, owner=portfolio_db.owner, securities=[]
        )

    async def __get_portfolio_securities(self, portfolio_id: int) -> list[SecurityWithVolumeAndPriceOutSchema]:
        """
        Приватный метод для получения акций портфеля
        """
        transactions = await self.transaction_repository.get_transaction_by_portfolio_id(portfolio_id)

        # Словарь {Тикер: [Количество акций в портфеле, Сумма цен акций, актуальных на момент покупки]}
        tickers_to_volume = dict()
        for transaction in transactions:
            if transaction.security not in tickers_to_volume:
                tickers_to_volume[transaction.security] = [transaction.volume, transaction.price * transaction.volume]
                continue
            current = tickers_to_volume[transaction.security]
            tickers_to_volume[transaction.security] = [
                current[0] + transaction.volume,
                current[1] + transaction.price * transaction.volume,
            ]

        # Массив тикеров акций, объем которых больше нуля
        tickers = []
        for security in tickers_to_volume:
            if tickers_to_volume[security][0] > 0:
                tickers.append(security)

        securities = [
            SecurityWithVolumeAndPriceOutSchema(
                ticker=security.ticker,
                name=security.name,
                price=round(tickers_to_volume[security.ticker][1] / tickers_to_volume[security.ticker][0], 2),
                # Средняя цена одной акции
                volume=tickers_to_volume[security.ticker][0],
                delta_price=round(
                    (security.price - tickers_to_volume[security.ticker][1] / tickers_to_volume[security.ticker][0])
                    * tickers_to_volume[security.ticker][0],
                    2,
                ),
            )
            for security in await self.securities_repository.get_securities_by_tickers(tickers)
        ]

        return securities

    async def get_portfolio_by_id(
        self, portfolio_id: int, user_id: int, include_securities: bool
    ) -> PortfolioOutSchema:
        portfolio = await self.repository.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            raise PortfolioNotFoundError(id=portfolio_id)
        if portfolio.owner != user_id:
            raise AccessDeniedException("You're not the owner of portfolio")

        if not include_securities:
            return PortfolioOutSchema(
                id=portfolio.id, balance=portfolio.balance, owner=portfolio.owner, securities=None
            )

        securities = await self.__get_portfolio_securities(portfolio_id)

        return PortfolioOutSchema(
            id=portfolio.id, balance=portfolio.balance, owner=portfolio.owner, securities=securities
        )

    async def get_portfolios_by_owner_id(self, owner_id: int, include_securities: bool) -> list[PortfolioOutSchema]:
        portfolios_id = await self.repository.get_portfolios_ids_by_owner_id(owner_id=owner_id)
        return [
            await self.get_portfolio_by_id(portfolio_id, owner_id, include_securities) for portfolio_id in portfolios_id
        ]

    async def delete_portfolio_by_id(self, portfolio_id: int, user_id: int) -> None:
        portfolio = await self.repository.get_portfolio_by_id(portfolio_id)
        if portfolio is None:
            raise PortfolioNotFoundError(id=portfolio_id)
        if portfolio.owner != user_id:
            raise AccessDeniedException("You're not the owner of portfolio")
        if len(await self.__get_portfolio_securities(portfolio_id)) > 0:
            raise ValidationException("Portfolio is not emtpy")

        await self.repository.delete_portfolio_by_id(portfolio_id)
        await self.user_repository.add_delta_to_user_balance(user_id, -1 * portfolio.balance)

    async def update_portfolio_balance(
        self, portfolio_id: int, new_balance: float, user_id: int
    ) -> PortfolioBalanceSchema:
        portfolio = await self.repository.get_portfolio_by_id(portfolio_id)
        if new_balance < 0:
            raise ConflictingStateException("Balance of the portfolio must be greater than 0")

        if portfolio is None:
            raise PortfolioNotFoundError(id=portfolio_id)
        if portfolio.owner != user_id:
            raise AccessDeniedException("You're not the owner of portfolio")

        new_user_balance = await self.user_repository.add_delta_to_user_balance(
            user_id=user_id, delta=new_balance - portfolio.balance
        )

        if new_user_balance < 0:
            raise ConflictingStateException("Balance of the user must be greater than 0")

        new_portfolio_balance = await self.repository.update_portfolio_balance(portfolio=portfolio, balance=new_balance)

        return PortfolioBalanceSchema(portfolio_balance=new_portfolio_balance, user_balance=new_user_balance)
