from datetime import datetime

from db.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class UserNotification(Base):
    __tablename__ = "user_notification"

    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    last_commit: Mapped[datetime] = mapped_column(nullable=True)
    open: Mapped[float] = mapped_column(nullable=True)
    close: Mapped[float] = mapped_column(nullable=True)
    take: Mapped[float] = mapped_column(nullable=True)
