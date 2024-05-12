from typing import Iterable

from db.base_repository import BaseRepository
from sqlalchemy import select
from transactions.models import Transactions
from transactions.schemas import TransactionCreateSchema


class TransactionsRepository(BaseRepository):
    async def create_transaction(self, transaction_schema: TransactionCreateSchema) -> Transactions:
        transaction_db = Transactions(**transaction_schema.model_dump())
        return await self.save(transaction_db)

    async def get_transaction_by_id(self, transaction_id: int) -> Iterable[Transactions]:
        statement = select(Transactions).where(Transactions.id == transaction_id)
        return await self.all(statement)

    async def get_transaction_by_portfolio_id(self, portfolio_id: int) -> Iterable[Transactions]:
        statement = select(Transactions).where(Transactions.portfolio == portfolio_id)
        return await self.all(statement)
