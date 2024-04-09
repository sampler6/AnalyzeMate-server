from exceptions.base import ResourceNotFoundException


class SecurityNotFoundError(ResourceNotFoundException):
    template: str = "Security not found: ticker={ticker}"
