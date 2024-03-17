from pydantic import BaseModel


class BaseResponse(BaseModel):
    status_code: int
    description: str | None
