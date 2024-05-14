import logging
from typing import Annotated

from auth import User
from auth.user_manager import current_active_user
from db.base import redis_db
from fastapi import APIRouter, Depends
from services.user import UserService

from api.deps import get_user_service

UserServiceDeps = Annotated[UserService, Depends(get_user_service)]
UserDeps = Annotated[User, Depends(current_active_user)]

router = APIRouter()
logger = logging.getLogger("api")


@router.post("/subscribe/", response_model=None)
async def subscribe_to_notifications(registration_token: str, user: UserDeps) -> None:
    await redis_db.set(str(user.id) + "_token", registration_token, ex=86400)


@router.get("/subscribe/{ticker}/", response_model=None)
async def subscribe_to_notifications_by_ticker(ticker: str, user: UserDeps, service: UserServiceDeps) -> None:
    await service.subscribe_user_to_notification(ticker, user.id)


@router.get("/unsubscribe/{ticker}/", response_model=None)
async def unsubscribe_from_notifications_by_ticker(ticker: str, user: UserDeps, service: UserServiceDeps) -> None:
    await service.unsubscribe_user_from_notification(ticker, user.id)
