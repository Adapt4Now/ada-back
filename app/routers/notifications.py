from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.schemas.notification import NotificationResponse, NotificationCreate
from app.services import NotificationService
from app.crud.notification import NotificationRepository

router = APIRouter()


def get_notification_service(
    db: AsyncSession = Depends(get_database_session),
) -> NotificationService:
    repo = NotificationRepository(db)
    return NotificationService(repo)


@router.get("/users/{user_id}/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    user_id: int,
    service: NotificationService = Depends(get_notification_service),
):
    return await service.get_notifications(user_id)


@router.post(
    "/users/{user_id}/notifications",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    user_id: int,
    data: NotificationCreate,
    service: NotificationService = Depends(get_notification_service),
):
    return await service.create_notification(user_id, data)


@router.post(
    "/users/notifications/read/{notification_id}",
    response_model=NotificationResponse,
)
async def mark_notification_as_read(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
):
    return await service.mark_as_read(notification_id)


@router.delete(
    "/users/notifications/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_notification(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
):
    await service.delete_notification(notification_id)
