import logging
from typing import Annotated

from auth import User
from auth.user_manager import current_active_user
from fastapi import APIRouter, Depends
from portfolio.schemas import PortfolioBalanceSchema, PortfolioInSchema, PortfolioOutSchema
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


@router.get("/", response_model=list[PortfolioOutSchema])
async def get_user_portfolios(
    include_securities: bool, service: PortfolioServiceDeps, user: UserDeps
) -> list[PortfolioOutSchema]:
    """
    Получить портфели текущего пользователя
    """
    return await service.get_portfolios_by_owner_id(user.id, include_securities)


@router.get("/{portfolio_id}/", response_model=PortfolioOutSchema)
async def get_portfolio_by_id(
    portfolio_id: int, service: PortfolioServiceDeps, include_securities: bool, user: UserDeps
) -> PortfolioOutSchema:
    """
    Получить портфель по id
    """
    return await service.get_portfolio_by_id(portfolio_id, user.id, include_securities)


@router.delete("/{portfolio_id}/", response_model=None)
async def delete(portfolio_id: int, service: PortfolioServiceDeps, user: UserDeps) -> None:
    """
    Удалить портфель по id
    """
    return await service.delete_portfolio_by_id(portfolio_id, user.id)


@router.patch("/{portfolio_id}/", response_model=PortfolioOutSchema)
async def update_portfolio_balance(
    portfolio_id: int, new_balance: float, service: PortfolioServiceDeps, user: UserDeps
) -> PortfolioBalanceSchema:
    """
    Обновить баланс портфеля(+ баланс пользователя)
    """
    return await service.update_portfolio_balance(portfolio_id, new_balance, user.id)
