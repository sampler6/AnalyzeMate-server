from datetime import datetime
from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr

"""id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    balance: Mapped[float] = mapped_column(nullable=False, default=0)
    patronymic: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    surname: Mapped[str] = mapped_column(nullable=True)
    birthdate: Mapped[datetime] = mapped_column(nullable=False)
    options: Mapped[str] = mapped_column(nullable=True)"""


class UserRead(schemas.BaseUser[int]):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserCreate(schemas.BaseUserCreate):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    balance: Optional[float] = None
    patronymic: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    birthdate: Optional[datetime] = None
    options: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserUpdate(schemas.BaseUserUpdate):
    pass
