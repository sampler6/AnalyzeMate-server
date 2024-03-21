from datetime import datetime

from db.base import Base
from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    Price: Mapped[float]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
