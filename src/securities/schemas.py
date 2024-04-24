from typing import Optional

from pydantic import BaseModel, Field
from tinkoff.invest import CandleInterval


class HistoricCandlesSchema(BaseModel):
    open: float
    close: float
    highest: float
    lowest: float
    volume: int
    ticker: str
    timeframe: CandleInterval
    timestamp: float


class HistoricCandlesOutSchema(BaseModel):
    open: float
    close: float
    highest: float
    lowest: float
    volume: int
    ticker: str
    timeframe: int
    timestamp: float


class SecurityOutSchema(BaseModel):
    ticker: str
    name: str
    historic_candles: Optional[list[HistoricCandlesOutSchema]] = Field(default=None)


class SecurityInSchema(BaseModel):
    ticker: str
    name: str
