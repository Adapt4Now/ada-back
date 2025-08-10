from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


class NotificationRepository:
    """Repository for managing notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: int) -> List[Notification]:
        result = await self.db.execute(
            select(Notification).where(Notification.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, data: NotificationCreate) -> Notification:
        notification = Notification(**data.model_dump())
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if notification is None:
            return None
        notification.is_read = True
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def delete(self, notification_id: int) -> bool:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if notification is None:
            return False
        await self.db.delete(notification)
        await self.db.commit()
        return True
