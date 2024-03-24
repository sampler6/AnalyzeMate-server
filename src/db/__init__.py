from typing import AsyncGenerator

from auth.models.user import User
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from securities import models as securities_models
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.base import Base

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):  # type: ignore
    yield SQLAlchemyUserDatabase(session, User)  # type: ignore


__all__ = (*securities_models.__all__, "Base")
