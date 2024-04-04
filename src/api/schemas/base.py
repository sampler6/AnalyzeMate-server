from pydantic import BaseModel


class TestResponse(BaseModel):
    description: str | None
