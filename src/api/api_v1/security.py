import logging
from typing import Annotated

from auth import User
from auth.user_manager import current_active_user
from fastapi import APIRouter, Depends
from securities.schemas import SecurityOutSchema
from services.security import SecuritiesService

from api.deps import get_security_service

router = APIRouter()
logger = logging.getLogger("api")

SecurityServiceDeps = Annotated[SecuritiesService, Depends(get_security_service)]
UserDeps = Annotated[User, Depends(current_active_user)]


@router.get("/", response_model=list[SecurityOutSchema])
async def get_all_securities(
    include_historic_candles: bool, service: SecurityServiceDeps, user: UserDeps
) -> list[SecurityOutSchema]:
    return await service.get_all_securities()


@router.post("/", response_model=list[SecurityOutSchema])
async def get_securities_by_tickers(
    tickers: list[str], include_historic_candles: bool, service: SecurityServiceDeps, user: UserDeps
) -> list[SecurityOutSchema]:
    return await service.get_securities_by_tickers(tickers)
