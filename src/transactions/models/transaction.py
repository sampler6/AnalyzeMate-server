from datetime import datetime, timezone

from db.base import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    volume: Mapped[int]
    price: Mapped[float]
    security: Mapped[str] = mapped_column(String, ForeignKey("securities.ticker"))
    portfolio: Mapped[int] = mapped_column(Integer, ForeignKey("portfolio.id"))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
