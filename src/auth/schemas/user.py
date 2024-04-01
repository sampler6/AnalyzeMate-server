from datetime import datetime, timezone
from typing import Any, Optional

from fastapi_users import schemas
from pydantic import Field


class UserRead(schemas.BaseUser[int]):
    balance: float
    patronymic: str
    name: str
    surname: str
    birthdate: datetime
    config: Optional[dict[str, Any]]


class UserCreate(schemas.BaseUserCreate):
    balance: Optional[float]
    patronymic: str
    name: str
    surname: str
    birthdate: datetime = Field(default=datetime.now(timezone.utc))
    config: Optional[dict[str, Any]]


class UserUpdate(schemas.BaseUserUpdate):
    balance: Optional[float]
    patronymic: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    birthdate: Optional[datetime]
    config: Optional[dict[str, Any]]
