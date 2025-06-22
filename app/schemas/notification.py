from datetime import datetime
from typing import Annotated, List
from pydantic import BaseModel, Field, ConfigDict


class NotificationBase(BaseModel):
    message: str = Field(..., description="Notification message")


class NotificationCreate(NotificationBase):
    user_id: Annotated[int, Field(gt=0)]


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
