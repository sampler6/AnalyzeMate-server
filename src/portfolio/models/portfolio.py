from db import Base
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column


class Portfolio(Base):
    __tablename__ = "portfolio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    balance: Mapped[float]
    owner: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
