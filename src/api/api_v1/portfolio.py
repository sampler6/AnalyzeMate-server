import logging
from typing import Annotated

from auth import User
from auth.user_manager import current_active_user
from fastapi import APIRouter, Depends
from portfolio.schemas import PortfolioInSchema, PortfolioOutSchema
from services.portfolio import PortfolioService

from api.deps import get_portfolio_service

router = APIRouter()
logger = logging.getLogger("api")

UserDeps = Annotated[User, Depends(current_active_user)]
PortfolioServiceDeps = Annotated[PortfolioService, Depends(get_portfolio_service)]


@router.post("/")
async def create_portfolio(
    new_portfolio: PortfolioInSchema, service: PortfolioServiceDeps, user: UserDeps
) -> PortfolioOutSchema:
    return await service.save_portfolio(new_portfolio, user)
