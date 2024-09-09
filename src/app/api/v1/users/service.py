import app.db.orm as orm
import app.api.v1.users.schema as schema
from app.core.base_repository import BaseRepository
from app.db.session import get_async_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class UserService(BaseRepository[orm.User]):
    def __init__(self, session: AsyncSession = Depends(get_async_session)) -> None:
        super().__init__(orm.User, session)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[orm.User]:
        return await super().get_all(skip, limit)

    async def get_by_id(self, id: int) -> orm.User:
        return await super().get_by_id(id)

    async def create(self, user: schema.UserCreate) -> orm.User:
        return await super().create(user)

    async def update(self, id: int, user: schema.UserUpdate) -> orm.User:
        return await super().update(id, user)

    async def delete(self, id: int) -> None:
        return await super().delete(id)
