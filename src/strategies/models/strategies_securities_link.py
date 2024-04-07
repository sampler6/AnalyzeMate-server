from db import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class StrategiesSecuritiesLink(Base):
    __tablename__ = "strategies_securities_link"

    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategies.id"))
    ticker: Mapped[str] = mapped_column(ForeignKey("securities.ticker"))
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolio.id"))
