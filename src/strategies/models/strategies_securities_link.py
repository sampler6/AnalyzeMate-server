from db.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class StrategiesSecuritiesLink(Base):
    __tablename__ = "strategies_securities_link"

    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategies.id"), primary_key=True)
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"), primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolio.id"), primary_key=True)
