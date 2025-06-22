from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SettingUpdate(BaseModel):
    theme: Optional[str] = Field(None, max_length=50)
    notifications_enabled: Optional[bool] = None


class SettingResponse(BaseModel):
    user_id: int
    theme: str
    notifications_enabled: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
