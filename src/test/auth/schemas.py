from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    balance: float
    patronymic: str
    name: str
    surname: str
    birthdate: datetime = Field(default=datetime.now(timezone.utc))
    config: Optional[dict[str, Any]]
