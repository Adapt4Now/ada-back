from typing import List

from typing import List

from app.domain.notifications.schemas import NotificationResponse, NotificationCreate
from app.core.exceptions import NotificationNotFoundError
from app.database import UnitOfWork


class NotificationService:
    """Service layer for notification-related operations."""

    def __init__(self, repo_factory, uow: UnitOfWork):
        self.repo_factory = repo_factory
        self.uow = uow

    async def get_notifications(self, user_id: int) -> List[NotificationResponse]:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            notifications = await repo.get_by_user(user_id)
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def create_notification(
        self, user_id: int, data: NotificationCreate
    ) -> NotificationResponse:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            notification = await repo.create(
                NotificationCreate(user_id=user_id, message=data.message)
            )
        return NotificationResponse.model_validate(notification)

    async def mark_as_read(self, notification_id: int) -> NotificationResponse:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            notification = await repo.mark_as_read(notification_id)
            if notification is None:
                raise NotificationNotFoundError()
        return NotificationResponse.model_validate(notification)

    async def delete_notification(self, notification_id: int) -> None:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            success = await repo.delete(notification_id)
        if not success:
            raise NotificationNotFoundError()
