from auth import User
from db.base_repository import BaseRepository
from sqlalchemy import select, update


class UserRepository(BaseRepository):
    async def add_delta_to_user_balance(self, user_id: int, delta: float) -> float | None:
        """
        Изменяет баланс пользователя на величину delta
        """
        statement = (
            update(User)
            .where(User.id == user_id)
            .values(balance=select(User.balance).where(User.id == user_id) + delta)
            .returning(User.balance)
        )  # type: ignore

        return await self.one_or_none(statement)
