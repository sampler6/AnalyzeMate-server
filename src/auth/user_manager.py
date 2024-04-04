from typing import AsyncGenerator, Optional

from config import SECRET
from db.base import get_async_session
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.db import BaseUserDatabase
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from auth import auth_backend
from auth.models.user import User


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):  # type: ignore
    reset_password_token_secret = SECRET  # type: ignore
    verification_token_secret = SECRET  # type: ignore

    async def on_after_register(self, user: User, request: Optional[Request] = None) -> None:
        print(f"User {user.id} has registered.")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None) -> None:
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):  # type: ignore
    yield SQLAlchemyUserDatabase(session, User)  # type: ignore


async def get_user_manager(
    user_db: BaseUserDatabase[User, int] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)  # type: ignore


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
