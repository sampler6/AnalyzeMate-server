from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from securities import models as securities_models
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from db.base import Base

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

__all__ = (*securities_models.__all__, "Base")
