from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from fastapi_users import schemas
from pydantic import BeforeValidator, Field


def password_validator(password: str) -> str:
    assert len(password) >= 8, "Password must have 8 or greater symbols"
    has_capital_letter: bool = False
    has_numeric_symbol: bool = False
    for symbol in password:
        if symbol.isnumeric():
            has_numeric_symbol = True
        elif symbol.isupper():
            has_capital_letter = True
    assert has_capital_letter, "Password must have capital letter"
    assert has_numeric_symbol, "Password must have numeric symbol"
    return password


class UserRead(schemas.BaseUser[int]):
    balance: float
    patronymic: str
    name: str
    surname: str
    birthdate: datetime = Field(default=datetime.now(timezone.utc))
    config: Optional[dict[str, Any]]


class UserCreate(schemas.BaseUserCreate):
    password: Annotated[str, BeforeValidator(password_validator)]
    balance: Optional[float]
    patronymic: str
    name: str
    surname: str
    birthdate: datetime = Field(default=datetime.now(timezone.utc))
    config: Optional[dict[str, Any]]


class UserUpdate(schemas.BaseUserUpdate):
    patronymic: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    birthdate: Optional[datetime] = Field(default=datetime.now(timezone.utc))
    config: Optional[dict[str, Any]]
