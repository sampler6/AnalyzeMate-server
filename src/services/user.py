from uuid import UUID

from exceptions.securities import SecurityNotFoundError
from repositories.security import SecuritiesRepository
from repositories.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
        self.securities_repository = SecuritiesRepository(session)

    async def subscribe_user_to_notification(self, ticker: str, user_id: UUID) -> None:
        security = await self.securities_repository.get_security_by_ticker(ticker)
        if not security:
            raise SecurityNotFoundError(ticker=ticker)

        await self.repository.subscribe_user_to_notifications(ticker, user_id)

    async def unsubscribe_user_from_notification(self, ticker: str, user_id: UUID) -> None:
        security = await self.securities_repository.get_security_by_ticker(ticker)
        if not security:
            raise SecurityNotFoundError(ticker=ticker)

        await self.repository.unsubscribe_user_from_notifications(ticker, user_id)
