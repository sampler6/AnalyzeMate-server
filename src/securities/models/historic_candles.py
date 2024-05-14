from db.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class HistoricCandles(Base):
    __tablename__ = "historic_candle"

    open: Mapped[float]
    close: Mapped[float]
    highest: Mapped[float]
    lowest: Mapped[float]
    volume: Mapped[int]
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"), primary_key=True)
    timeframe: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[float] = mapped_column(primary_key=True)
