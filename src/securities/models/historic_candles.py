from datetime import datetime

from db.base import Base
from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column


class HistoricCandles(Base):
    __tablename__ = "historic_candle"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    open: Mapped[float]
    close: Mapped[float]
    highest: Mapped[float]
    lowest: Mapped[float]
    volume: Mapped[int]
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"))
    timeframe: Mapped[int]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
