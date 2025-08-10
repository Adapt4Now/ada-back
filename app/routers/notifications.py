from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.crud.notification import NotificationRepository
from app.schemas.notification import NotificationResponse, NotificationCreate
from app.core.exceptions import NotificationNotFoundError

router = APIRouter()


def get_notification_repository(
    db: AsyncSession = Depends(get_database_session),
) -> NotificationRepository:
    return NotificationRepository(db)


@router.get("/users/{user_id}/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    user_id: int,
    repo: NotificationRepository = Depends(get_notification_repository),
):
    notifications = await repo.get_by_user(user_id)
    return [NotificationResponse.model_validate(n) for n in notifications]


@router.post(
    "/users/{user_id}/notifications",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    user_id: int,
    data: NotificationCreate,
    repo: NotificationRepository = Depends(get_notification_repository),
):
    notification = await repo.create(
        NotificationCreate(user_id=user_id, message=data.message)
    )
    return NotificationResponse.model_validate(notification)


@router.post(
    "/users/notifications/read/{notification_id}",
    response_model=NotificationResponse,
)
async def mark_notification_as_read(
    notification_id: int,
    repo: NotificationRepository = Depends(get_notification_repository),
):
    notification = await repo.mark_as_read(notification_id)
    if notification is None:
        raise NotificationNotFoundError()
    return NotificationResponse.model_validate(notification)


@router.delete(
    "/users/notifications/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_notification(
    notification_id: int,
    repo: NotificationRepository = Depends(get_notification_repository),
):
    success = await repo.delete(notification_id)
    if not success:
        raise NotificationNotFoundError()
