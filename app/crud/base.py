from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic repository providing basic CRUD operations."""

    model: Type[ModelType]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, obj_id: int) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.db.execute(
            select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, data: dict) -> ModelType:
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj_id: int, data: dict) -> Optional[ModelType]:
        obj = await self.get(obj_id)
        if obj is None:
            return None
        for field, value in data.items():
            setattr(obj, field, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj_id: int) -> Optional[ModelType]:
        obj = await self.get(obj_id)
        if obj is None:
            return None
        await self.db.delete(obj)
        await self.db.commit()
        return obj
