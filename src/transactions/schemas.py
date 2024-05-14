from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class TransactionType(StrEnum):
    Buy = "Buy"
    Sell = "Sell"


class TransactionCreateSchema(BaseModel):
    volume: int
    price: float
    security: str
    portfolio: int
    timestamp: datetime = Field(default=datetime.now(timezone.utc))


class TransactionInSchema(BaseModel):
    volume: int = Field(gt=0)
    security: str
    portfolio: int


class TransactionOutSchema(BaseModel):
    volume: int
    price: float
    security: str
    portfolio: int
    type: TransactionType
    timestamp: datetime = Field(default=datetime.now(timezone.utc))
