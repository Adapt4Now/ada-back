from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


async def get_notifications(db: AsyncSession, user_id: int) -> List[Notification]:
    result = await db.execute(select(Notification).where(Notification.user_id == user_id))
    return list(result.scalars().all())


async def create_notification(db: AsyncSession, data: NotificationCreate) -> Notification:
    notification = Notification(**data.model_dump())
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_as_read(db: AsyncSession, notification_id: int) -> Optional[Notification]:
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notification = result.scalar_one_or_none()
    if notification is None:
        return None
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


async def delete_notification(db: AsyncSession, notification_id: int) -> bool:
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notification = result.scalar_one_or_none()
    if notification is None:
        return False
    await db.delete(notification)
    await db.commit()
    return True
