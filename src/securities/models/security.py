from db.base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Securities(Base):
    __tablename__ = "securities"

    ticker: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str]
    price: Mapped[float]
