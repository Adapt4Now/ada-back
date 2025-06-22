from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.crud.notification import (
    get_notifications as crud_get_notifications,
    create_notification as crud_create_notification,
    mark_as_read as crud_mark_as_read,
    delete_notification as crud_delete_notification,
)
from app.schemas.notification import NotificationResponse, NotificationCreate

router = APIRouter()


@router.get("/users/{user_id}/notifications", response_model=List[NotificationResponse])
async def get_notifications(user_id: int, db: AsyncSession = Depends(get_database_session)):
    notifications = await crud_get_notifications(db, user_id)
    return [NotificationResponse.model_validate(n) for n in notifications]


@router.post(
    "/users/{user_id}/notifications",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(user_id: int, data: NotificationCreate, db: AsyncSession = Depends(get_database_session)):
    notification = await crud_create_notification(
        db,
        NotificationCreate(user_id=user_id, message=data.message),
    )
    return NotificationResponse.model_validate(notification)


@router.post("/users/notifications/read/{notification_id}", response_model=NotificationResponse)
async def mark_notification_as_read(notification_id: int, db: AsyncSession = Depends(get_database_session)):
    notification = await crud_mark_as_read(db, notification_id)
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return NotificationResponse.model_validate(notification)


@router.delete("/users/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: int, db: AsyncSession = Depends(get_database_session)):
    success = await crud_delete_notification(db, notification_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
