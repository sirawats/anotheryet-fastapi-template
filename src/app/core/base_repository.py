from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import re
from uuid import UUID
from asyncpg import ForeignKeyViolationError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Type, TypeVar, Generic
from typing import List
from sqlalchemy.exc import IntegrityError


T = TypeVar("T")

ID = int | str | UUID


class IAsyncRepository(ABC):
    """
    Abstract base class defining the interface for asynchronous repositories.
    """

    @abstractmethod
    async def get_all(self, skip: int, limit: int):
        """Retrieve all items with pagination."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: ID):
        """Retrieve an item by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, item):
        """Create a new item."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: ID, item):
        """Update an existing item."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: ID):
        """Delete an item by its ID."""
        raise NotImplementedError


class GenericAsyncRepository(IAsyncRepository, Generic[T]):
    """
    Generic implementation of IAsyncRepository for SQLAlchemy ORM models.

    Example use:
        ```
        class UserRepository(GenericAsyncRepository[orm.User]):
            pass
        ```
    """

    orm_model: Type[T]
    session: AsyncSession

    def __init__(self, orm_model: Type[T], session: AsyncSession):
        """
        Initialize the repository with an ORM model and database session.
        """
        self.session = session
        self.orm_model = orm_model

    @staticmethod
    def __table_name_from_message(error_message: str) -> str | None:
        """
        Extract table name from an error message.
        """
        pattern = r'table "(.+?)"'
        match = re.search(pattern, error_message)
        return match.group(1) if match else None

    @asynccontextmanager
    async def transaction(self, autocommit: bool = True):
        """
        Context manager for database transactions.
        """
        try:
            yield
            if autocommit:
                await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Retrieve all items with pagination.
        """
        result = await self.session.execute(select(self.orm_model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, id: ID) -> T | None:
        """
        Retrieve an item by its ID.
        """
        if not hasattr(self.orm_model, "id"):
            raise AttributeError(f"{self.orm_model.__name__} must have an 'id' attribute")
        result = await self.session.execute(select(self.orm_model).filter(getattr(self.orm_model, "id") == id))
        return result.scalar_one_or_none()

    async def create(self, item: BaseModel) -> T:
        """
        Create a new item.
        """
        try:
            actual_item = self.orm_model(**item.model_dump())
            self.session.add(actual_item)
            await self.session.commit()
            await self.session.refresh(actual_item)
            return actual_item
        except IntegrityError as alchemy_error:
            await self.session.rollback()
            if isinstance(alchemy_error.orig, ForeignKeyViolationError):
                table_name = self.__table_name_from_message(str(alchemy_error.orig))
                if isinstance(table_name, str):
                    formatted = " ".join(table_name.split("_"))
                    raise ValueError(f"{formatted} id does not exist")
            raise

    async def create_many(self, items: List[BaseModel]) -> List[T]:
        """
        Create multiple items at once.
        """
        try:
            actual_items = [self.orm_model(**item.model_dump()) for item in items]
            self.session.add_all(actual_items)
            await self.session.commit()
            return actual_items
        except IntegrityError as alchemy_error:
            await self.session.rollback()
            if isinstance(alchemy_error.orig, ForeignKeyViolationError):
                table_name = self.__table_name_from_message(str(alchemy_error.orig))
                if isinstance(table_name, str):
                    formatted = " ".join(table_name.split("_"))
                    raise ValueError(f"{formatted} id does not exist")
            raise

    async def update(self, id: ID, item: BaseModel) -> T:
        """
        Update an existing item.
        """
        db_item = await self.get_by_id(id)
        if not db_item:
            raise ValueError(f"Item with id {id} not found")

        update_data = item.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)

        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def delete(self, id: ID) -> None:
        """
        Delete an item by its ID.
        """
        db_item = await self.get_by_id(id)
        if not db_item:
            raise ValueError(f"Item with id {id} not found")

        await self.session.delete(db_item)
        await self.session.commit()
