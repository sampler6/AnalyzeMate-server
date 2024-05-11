from typing import Annotated

from auth import User
from auth.configuration import auth_backend
from auth.schemas.user import UserCreate, UserRead, UserUpdate
from auth.user_manager import current_active_user, fastapi_users
from db.base import get_async_session, redis_db
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from task.task_send_notification import send_notification

router = APIRouter()
UserDeps = Annotated[User, Depends(current_active_user)]

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)


router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])


@router.post("/subscribe/", response_model=None)
async def subscribe_to_notifications(registration_token: str, user: UserDeps) -> None:
    await redis_db.set(str(user.id) + "_token", registration_token, ex=86400)


@router.get("/send_test_notify/", response_model=None)
async def send_test_notify(session: AsyncSession = Depends(get_async_session)) -> None:
    stmt = select(User.id)
    result = (await session.execute(stmt)).scalars().all()
    send_notification.delay(result, "test", "test")
