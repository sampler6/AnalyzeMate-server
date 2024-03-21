from db.base import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Securities(Base):
    __tablename__ = "securities"

    figi: Mapped[str] = mapped_column(String, primary_key=True)
    ticker: Mapped[str] = mapped_column(String)
    name: Mapped[str]
    price_history: Mapped[int] = mapped_column(Integer, ForeignKey("price_history.id"))
    description: Mapped[str] = mapped_column(nullable=True)
