from db.base import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Securities(Base):
    __tablename__ = "securities"

    Ticker: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str]
    price_history: Mapped[int] = mapped_column(Integer, ForeignKey("price_history.id"))
    description: Mapped[str]
