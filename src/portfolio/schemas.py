from typing import Optional

from pydantic import BaseModel, Field
from securities.schemas import SecurityWithVolumeAndPriceOutSchema


class PortfolioInSchema(BaseModel):
    balance: float = Field(default=0.0, ge=0)


class PortfolioOutSchema(BaseModel):
    id: int
    balance: float
    owner: int

    securities: Optional[list[SecurityWithVolumeAndPriceOutSchema]]


class PortfolioBalanceSchema(BaseModel):
    portfolio_balance: float
    user_balance: float
