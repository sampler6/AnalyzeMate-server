from datetime import datetime, timezone
from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, Field
from tinkoff.invest import CandleInterval


def timeframe_validator(timeframe: CandleInterval) -> int:
    return timeframe.value


class HistoricCandlesSchema(BaseModel):
    open: float
    close: float
    highest: float
    lowest: float
    volume: int
    ticker: str
    timeframe: Annotated[int, BeforeValidator(timeframe_validator)]
    timestamp: datetime = Field(default=datetime.now(timezone.utc))


class SecurityOutSchema(BaseModel):
    ticker: str
    name: str
    historic_candles: Optional[list[HistoricCandlesSchema]] = Field(default=None)


class SecurityInSchema(BaseModel):
    ticker: str
    name: str
