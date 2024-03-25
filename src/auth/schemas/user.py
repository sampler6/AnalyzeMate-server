from datetime import datetime
from typing import Optional

from fastapi_users import schemas
from pydantic import Field


class UserRead(schemas.BaseUser[int]):
    balance: float
    patronymic: str
    name: str
    surname: str
    birthdate: datetime
    options: Optional[str]


class UserCreate(schemas.BaseUserCreate):
    balance: Optional[float]
    patronymic: str
    name: str
    surname: str
    birthdate: datetime = Field(default=datetime.utcnow())
    options: Optional[str]


class UserUpdate(schemas.BaseUserUpdate):
    balance: Optional[float]
    patronymic: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    birthdate: Optional[datetime]
    options: Optional[str]
