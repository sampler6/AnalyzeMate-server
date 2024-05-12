from exceptions.base import ResourceNotFoundException


class PortfolioNotFoundError(ResourceNotFoundException):
    template: str = "Portfolio not found: id={id}"
