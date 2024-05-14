from typing import Any

from db.base import Base
from sqlalchemy.dialects.mssql import JSON
from sqlalchemy.orm import Mapped, mapped_column


class Strategies(Base):
    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(primary_key=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSON)
