from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.notifications.models import Notification
from app.domain.notifications.schemas import NotificationCreate
from app.domain.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for managing notifications."""

    model = Notification

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user(self, user_id: int) -> List[Notification]:
        result = await self.session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, data: NotificationCreate) -> Notification:
        return await super().create(data.model_dump())

    async def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        notification = await self.get(notification_id)
        if notification is None:
            return None
        notification.is_read = True
        return notification

    async def delete(self, notification_id: int) -> bool:
        deleted = await super().delete(notification_id)
        return deleted is not None
