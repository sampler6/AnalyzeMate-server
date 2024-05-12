from datetime import datetime, timezone
from typing import Any

from exceptions.base import AccessDeniedException, ConflictingStateException, ValidationException
from exceptions.portfolio import PortfolioNotFoundError
from exceptions.securities import SecurityNotFoundError
from repositories.portfolio import PortfolioRepository
from repositories.security import SecuritiesRepository
from repositories.transaction import TransactionsRepository
from repositories.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from transactions.schemas import TransactionCreateSchema, TransactionInSchema, TransactionOutSchema, TransactionType


class TransactionsService:
    def __init__(self, session: AsyncSession):
        self.repository = TransactionsRepository(session)
        self.portfolio_repository = PortfolioRepository(session)
        self.securities_repository = SecuritiesRepository(session)
        self.user_repository = UserRepository(session)

    async def __get_portfolio_securities(self, portfolio_id: int) -> dict[str, tuple[int, float]]:
        """
        Приватный метод для получения акций портфеля.
        Проверка на существования портфеля проводиться вне метода.
        Возвращает словарь Тикер: Объем, сумма актуальных цен всех акций.
        """
        transactions = await self.repository.get_transaction_by_portfolio_id(portfolio_id)

        # Словарь {Тикер: [Количество акций в портфеле, Сумма цен акций, актуальных на момент покупки]}
        tickers_to_volume: dict[str, Any] = dict()
        for transaction in transactions:
            if transaction.security not in tickers_to_volume:
                tickers_to_volume[transaction.security] = (transaction.volume, transaction.price * transaction.volume)
                continue
            current = tickers_to_volume[transaction.security]
            tickers_to_volume[transaction.security] = [
                current[0] + transaction.volume,
                current[1] + transaction.price * transaction.volume,
            ]

        return tickers_to_volume

    async def make_transaction(
        self, transaction: TransactionInSchema, transaction_type: TransactionType, user_id: int
    ) -> TransactionOutSchema:
        portfolio = await self.portfolio_repository.get_portfolio_by_id(transaction.portfolio)
        if portfolio is None:
            raise PortfolioNotFoundError(id=transaction.portfolio)
        if portfolio.owner != user_id:
            raise AccessDeniedException("You're not the owner of portfolio")

        portfolio_securities = await self.__get_portfolio_securities(portfolio.id)
        current_volume = (
            portfolio_securities[transaction.security][0] if transaction.security in portfolio_securities else 0
        )
        security = await self.securities_repository.get_security_by_ticker(transaction.security)
        if not security:
            raise SecurityNotFoundError(ticker=transaction.security)

        if transaction_type == TransactionType.Sell and current_volume < transaction.volume:
            raise ConflictingStateException(f"User have only {current_volume} {transaction.security} shares")

        if transaction_type == TransactionType.Buy and transaction.volume * security.price > portfolio.balance:
            raise ValidationException("Portfolio balance is lesser than transaction price")

        transaction_create = TransactionCreateSchema(
            **transaction.model_dump()
            | {
                "volume": transaction.volume if transaction_type == TransactionType.Buy else -transaction.volume,
                "timestamp": datetime.now(timezone.utc),
                "price": security.price,
            }
        )
        await self.repository.create_transaction(transaction_create)

        if transaction_type == TransactionType.Sell:
            delta = round(transaction.volume * security.price, 2)
        else:
            delta = round(-transaction.volume * security.price, 2)

        await self.portfolio_repository.update_portfolio_balance(portfolio=portfolio, balance=portfolio.balance + delta)
        await self.user_repository.add_delta_to_user_balance(user_id=portfolio.owner, delta=delta)
        # TODO: Подпись на канал акции, если акции раньше не было

        return TransactionOutSchema(**transaction_create.model_dump())
