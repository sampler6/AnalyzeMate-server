import logging
from typing import Annotated

from auth import User
from auth.user_manager import current_active_user
from db.base import redis_db
from fastapi import APIRouter, Depends

UserDeps = Annotated[User, Depends(current_active_user)]

router = APIRouter()
logger = logging.getLogger("api")


@router.post("/subscribe/", response_model=None)
async def subscribe_to_notifications(registration_token: str, user: UserDeps) -> None:
    await redis_db.set(str(user.id) + "_token", registration_token, ex=86400)


@router.post("/subscribe/{ticker}/", response_model=None)
async def subscribe_to_notifications_by_ticker(registration_token: str, user: UserDeps) -> None:
    return None
