from datetime import datetime
from typing import Any

from db.base import Base
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)  # type: ignore
    email: Mapped[str] = mapped_column(unique=True)  # type: ignore
    balance: Mapped[float] = mapped_column(nullable=False, default=0)
    patronymic: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    surname: Mapped[str] = mapped_column(nullable=True)
    birthdate: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
