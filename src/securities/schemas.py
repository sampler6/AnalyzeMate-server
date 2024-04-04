from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class HistoricCandlesOutSchema(BaseModel):
    open: float
    close: float
    highest: float
    lowest: float
    volume: int
    timestamp: datetime = Field(default=datetime.now(timezone.utc))


class SecurityOutSchema(BaseModel):
    ticker: str
    name: str
    historic_candles: Optional[list[HistoricCandlesOutSchema]] = Field(default=None)
