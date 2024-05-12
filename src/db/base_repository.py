import abc
from typing import Any, Generic, Iterable, Optional, TypeVar

from sqlalchemy import Delete, Insert, Select, Update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(abc.ABC, Generic[T]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def all(self, statement: Select | Delete | Update | Insert) -> Iterable[Any]:
        return (await self.session.execute(statement)).scalars().all()

    async def one_or_none(self, statement: Select | Delete | Update | Insert) -> Optional[Any]:
        return (await self.session.execute(statement)).scalars().one_or_none()

    async def one(self, statement: Select | Delete | Update | Insert) -> Any:
        return (await self.session.execute(statement)).scalars().one()

    async def save(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def save_all(self, objects: list[T]) -> None:
        self.session.add_all(objects)

    async def remove(self, obj: T) -> None:
        return await self.session.delete(obj)
