from typing import List
import logging

from app.domain.notifications.schemas import NotificationResponse, NotificationCreate
from app.core.exceptions import NotificationNotFoundError
from app.database import UnitOfWork

logger = logging.getLogger(__name__)


class NotificationService:
    """Service layer for notification-related operations."""

    def __init__(self, repository_factory, unit_of_work: UnitOfWork):
        self.repository_factory = repository_factory
        self.unit_of_work = unit_of_work

    async def get_notifications(self, user_id: int) -> List[NotificationResponse]:
        """Retrieve notifications for a user."""
        async with self.unit_of_work as unit_of_work:
            notification_repository = self.repository_factory(unit_of_work.session)
            notifications = await notification_repository.get_by_user(user_id)
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def create_notification(
        self, user_id: int, data: NotificationCreate
    ) -> NotificationResponse:
        """Create a notification for a user."""
        logger.info("Creating notification for user %s", user_id)
        async with self.unit_of_work as unit_of_work:
            notification_repository = self.repository_factory(unit_of_work.session)
            notification = await notification_repository.create(
                NotificationCreate(user_id=user_id, message=data.message)
            )
        logger.info("Created notification %s", notification.id)
        return NotificationResponse.model_validate(notification)

    async def mark_as_read(self, notification_id: int) -> NotificationResponse:
        """Mark a notification as read."""
        logger.info("Marking notification %s as read", notification_id)
        async with self.unit_of_work as unit_of_work:
            notification_repository = self.repository_factory(unit_of_work.session)
            notification = await notification_repository.mark_as_read(notification_id)
            if notification is None:
                raise NotificationNotFoundError()
        logger.info("Marked notification %s as read", notification_id)
        return NotificationResponse.model_validate(notification)

    async def delete_notification(self, notification_id: int) -> None:
        """Delete a notification."""
        logger.info("Deleting notification %s", notification_id)
        async with self.unit_of_work as unit_of_work:
            notification_repository = self.repository_factory(unit_of_work.session)
            success = await notification_repository.delete(notification_id)
        if not success:
            raise NotificationNotFoundError()
        logger.info("Deleted notification %s", notification_id)
