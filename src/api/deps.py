from db.base import get_async_session
from fastapi import Depends
from services.security import SecurityService
from sqlalchemy.ext.asyncio import AsyncSession


async def get_security_service(session: AsyncSession = Depends(get_async_session)) -> SecurityService:
    return SecurityService(session=session)
