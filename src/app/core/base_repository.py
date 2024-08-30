from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import re
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, Type, TypeVar, Generic, Union
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert


T = TypeVar("T")


class IAsyncRepository(ABC):
    @abstractmethod
    async def get_all(self, skip: int, limit: int) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: Union[int, str, UUID]) -> T:
        raise NotImplementedError

    @abstractmethod
    async def create(self, item) -> T:
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: Union[int, str, UUID], item) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: Union[int, str, UUID]):
        raise NotImplementedError


class GenericAsyncRepository(IAsyncRepository, Generic[T]):
    entity: Type[T]
    session: AsyncSession

    def __init__(self, entity: Type[T], session: AsyncSession):
        self.session = session
        self.entity = entity

    def __table_name_from_message(self, error_message):
        pattern = r'table "(.+?)"'

        match = re.search(pattern, error_message)

        if match is not None:
            return match.group(1)
        else:
            return None

    @asynccontextmanager
    async def transaction(self, autocommit=True):
        try:
            yield
            if autocommit:
                await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def get_all(self, skip: int, limit: int, only_id: Optional[bool] = False) -> List[T]:
        result = await self.session.execute(select(self.entity).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, id: Union[int, str, UUID]) -> T:
        if not hasattr(self.entity, "id"):
            raise AttributeError(f"{self.entity.__name__} must have an 'id' attribute")
        result = await self.session.execute(select(self.entity).filter(getattr(self.entity, "id") == id))
        return result.scalar_one()

    async def create(self, item: BaseModel) -> T:
        try:
            actual_item = self.entity(**item.dict())

            self.session.add(actual_item)
            await self.session.commit()
            await self.session.refresh(actual_item)

            return actual_item
        except IntegrityError as alchemy_error:
            if isinstance(alchemy_error.orig, errors.ForeignKeyViolation):
                table_name = self.__table_name_from_message(alchemy_error.orig.diag.message_detail)
                if isinstance(table_name, str):
                    formatted = " ".join(table_name.split("_"))
                    raise ValueError(f"{formatted} id does not exist")
            raise

    async def create_many(self, items: List[BaseModel]) -> List[T]:
        try:
            actual_items = [item.dict() for item in items]

            result = await self.session.scalars(insert(self.entity).returning(getattr(self.entity, "id")).values(actual_items))
            await self.session.commit()

            return list(result)
        except IntegrityError as alchemy_error:
            if isinstance(alchemy_error.orig, errors.ForeignKeyViolation):
                table_name = self.__table_name_from_message(alchemy_error.orig.diag.message_detail)
                if isinstance(table_name, str):
                    formatted = " ".join(table_name.split("_"))
                    raise ValueError(f"{formatted} id does not exist")
            raise

    async def update(self, id: Union[int, str, UUID], item: BaseModel) -> T:
        result = await self.session.execute(select(self.entity).filter(getattr(self.entity, "id") == id))
        db_item = result.scalar_one()

        actual_item = item.dict(exclude_unset=True)

        for key, value in actual_item.items():
            setattr(db_item, key, value)
        await self.session.commit()
        await self.session.refresh(db_item)

        return db_item

    async def delete(self, id: Union[int, str, UUID]):
        result = await self.session.execute(select(self.entity).filter(getattr(self.entity, "id") == id))
        db_item = result.scalar_one()

        await self.session.delete(db_item)
        await self.session.commit()
