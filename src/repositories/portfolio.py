from db.base_repository import BaseRepository
from portfolio.models import Portfolio
from portfolio.schemas import PortfolioInSchema


class PortfolioRepository(BaseRepository):
    async def save_portfolio(self, portfolio: PortfolioInSchema, owner: int) -> Portfolio:
        result = await self.save(Portfolio(**portfolio.model_dump() | {"owner": owner}))
        await self.session.commit()
        return result
