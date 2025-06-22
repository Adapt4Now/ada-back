from typing import List, Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class TaskBaseSchema(BaseModel):
    """Base task model with main fields."""
    title: str = Field(min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(
        default=None,
        description="Optional task description"
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Task priority from 1 to 5"
    )

    class Config:
        from_attributes = True


class TaskCreateSchema(TaskBaseSchema):
    """Schema for creating a new task."""
    pass


class TaskUpdateSchema(BaseModel):
    """Schema for updating task information."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_completed: Optional[bool] = None
    assigned_user_id: Optional[int] = Field(None, gt=0)

    class Config:
        from_attributes = True


class TaskResponseSchema(TaskBaseSchema):
    """Schema for task response with additional fields."""
    id: int = Field(gt=0, description="Task unique identifier")
    is_completed: bool = Field(
        default=False,
        description="Indicates if the task is completed"
    )
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    assigned_user_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID of the user assigned to this task"
    )

class TaskAssignGroupsSchema(BaseModel):
    """Schema for assigning task to groups."""
    group_ids: Annotated[List[int], Field(min_length=1)]

    model_config = ConfigDict(frozen=True)

