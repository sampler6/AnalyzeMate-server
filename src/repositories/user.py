import logging
from uuid import UUID

from auth import User
from auth.models import UserNotification
from db.base_repository import BaseRepository
from sqlalchemy import and_, delete, select, update

logger = logging.getLogger("api")


class UserRepository(BaseRepository):
    async def add_delta_to_user_balance(self, user_id: int, delta: float) -> float:
        """
        Изменяет баланс пользователя на величину delta
        """
        statement = select(User.balance).where(User.id == user_id)

        old_balance = await self.one(statement)

        statement = update(User).where(User.id == user_id).values(balance=old_balance + delta).returning(User.balance)

        return (await self.session.execute(statement)).scalars().one()

    async def is_user_exists(self, user_id: int) -> bool:
        statement = select(User.id).where(User.id == user_id)
        result = await self.one_or_none(statement)
        return bool(result)

    async def subscribe_user_to_notifications(self, ticker: str, user_id: UUID) -> None:
        user_notification = UserNotification(ticker=ticker, user_id=user_id)
        self.session.add(user_notification)

    async def unsubscribe_user_from_notifications(self, ticker: str, user_id: UUID) -> None:
        statement = delete(UserNotification).where(
            and_(UserNotification.ticker == ticker, UserNotification.user_id == user_id)
        )
        await self.session.execute(statement)
