import logging
from typing import Annotated

from auth import User
from auth.user_manager import current_active_user
from db.base import get_async_session, redis_db
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from task.task_send_notification import send_notification

UserDeps = Annotated[User, Depends(current_active_user)]

router = APIRouter()
logger = logging.getLogger("api")

# TODO: Удалить. Встроить в авторизацию посылку токена в авторизацию. "Подписка через покупку" акции


@router.post("/subscribe/", response_model=None)
async def subscribe_to_notifications(registration_token: str, user: UserDeps) -> None:
    await redis_db.set(str(user.id) + "_token", registration_token, ex=86400)


@router.get("/send_test_notify/", response_model=None)
async def send_test_notify(session: AsyncSession = Depends(get_async_session)) -> None:
    stmt = select(User.id)
    result = (await session.execute(stmt)).scalars().all()
    send_notification.delay(result, "test", "test")
