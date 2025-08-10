from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AchievementBaseSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True


class AchievementCreateSchema(AchievementBaseSchema):
    pass


class AchievementUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

    class Config:
        from_attributes = True


class AchievementResponseSchema(AchievementBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
