from auth import User
from db.base_repository import BaseRepository
from sqlalchemy import select


class UserRepository(BaseRepository):
    async def is_user_exists(self, user_id: int) -> bool:
        statement = select(User.id).where(User.id == user_id)
        result = await self.one_or_none(statement)
        return bool(result)
