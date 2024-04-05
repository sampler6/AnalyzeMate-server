from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class HistoricCandlesSchema(BaseModel):
    open: float
    close: float
    highest: float
    lowest: float
    volume: int
    ticker: str
    timestamp: datetime = Field(default=datetime.now(timezone.utc))


class SecurityOutSchema(BaseModel):
    ticker: str
    name: str
    historic_candles: Optional[list[HistoricCandlesSchema]] = Field(default=None)


class SecurityInSchema(BaseModel):
    ticker: str
    name: str
