from datetime import datetime, timezone

from db import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    volume: Mapped[int]
    price: Mapped[int]
    security: Mapped[int] = mapped_column(Integer, ForeignKey("securities.id"))
    portfolio: Mapped[int] = mapped_column(Integer, ForeignKey("portfolio.id"))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
