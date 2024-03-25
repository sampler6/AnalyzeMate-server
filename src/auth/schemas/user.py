from datetime import datetime
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    balance: float
    patronymic: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    birthdate: Optional[datetime]
    options: Optional[str]


class UserCreate(schemas.BaseUserCreate):
    balance: Optional[float] = None
    patronymic: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    birthdate: Optional[datetime] = None
    options: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    balance: Optional[float] = None
    patronymic: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    birthdate: Optional[datetime] = None
    options: Optional[str] = None
