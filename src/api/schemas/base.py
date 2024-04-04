from pydantic import BaseModel


class BaseResponse(BaseModel):
    description: str | None
