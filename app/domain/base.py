from typing import Generic, List, Optional, Type, TypeVar, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class Repository(Protocol[ModelType]):
    async def get(self, entity_id: int) -> Optional[ModelType]: ...

    async def get_list(self, skip: int = 0, limit: int = 100) -> List[ModelType]: ...

    async def create(self, data: dict) -> ModelType: ...

    async def update(self, entity_id: int, data: dict) -> Optional[ModelType]: ...

    async def delete(self, entity_id: int) -> Optional[ModelType]: ...


class BaseRepository(Generic[ModelType], Repository[ModelType]):
    """Generic repository providing basic CRUD operations."""

    model: Type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, entity_id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.session.execute(
            select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, data: dict) -> ModelType:
        obj = self.model(**data)
        self.session.add(obj)
        return obj

    async def update(self, entity_id: int, data: dict) -> Optional[ModelType]:
        obj = await self.get(entity_id)
        if obj is None:
            return None
        for field, value in data.items():
            setattr(obj, field, value)
        return obj

    async def delete(self, entity_id: int) -> Optional[ModelType]:
        obj = await self.get(entity_id)
        if obj is None:
            return None
        await self.session.delete(obj)
        return obj


class BaseService(Generic[ModelType]):
    """Base service providing common CRUD operations."""

    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    async def get(self, *args, **kwargs):
        return await self.repository.get(*args, **kwargs)

    async def get_list(self, *args, **kwargs):
        return await self.repository.get_list(*args, **kwargs)

    async def create(self, *args, **kwargs):
        return await self.repository.create(*args, **kwargs)

    async def update(self, *args, **kwargs):
        return await self.repository.update(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        return await self.repository.delete(*args, **kwargs)
