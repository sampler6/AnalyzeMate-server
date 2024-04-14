from pydantic import BaseModel, Field


class PortfolioInSchema(BaseModel):
    balance: float = Field(default=0.0)


class PortfolioOutSchema(BaseModel):
    id: int
    balance: float
    owner: int
