from typing import List

from typing import List

from app.domain.notifications.repository import NotificationRepository
from app.domain.notifications.schemas import NotificationResponse, NotificationCreate
from app.core.exceptions import NotificationNotFoundError


class NotificationService:
    """Service layer for notification-related operations."""

    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def get_notifications(self, user_id: int) -> List[NotificationResponse]:
        notifications = await self.repo.get_by_user(user_id)
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def create_notification(
        self, user_id: int, data: NotificationCreate
    ) -> NotificationResponse:
        notification = await self.repo.create(
            NotificationCreate(user_id=user_id, message=data.message)
        )
        return NotificationResponse.model_validate(notification)

    async def mark_as_read(self, notification_id: int) -> NotificationResponse:
        notification = await self.repo.mark_as_read(notification_id)
        if notification is None:
            raise NotificationNotFoundError()
        return NotificationResponse.model_validate(notification)

    async def delete_notification(self, notification_id: int) -> None:
        success = await self.repo.delete(notification_id)
        if not success:
            raise NotificationNotFoundError()
