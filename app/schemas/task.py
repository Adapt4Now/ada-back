from typing import List, Optional, Annotated
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, field_validator
from pydantic import ConfigDict

UTC = ZoneInfo("UTC")


class TaskBaseSchema(BaseModel):
    """Base task model with main fields."""
    title: str = Field(min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(
        default=None,
        description="Optional task description",
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Task priority from 1 to 5",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Optional deadline for completing the task",
    )
    reward_points: int = Field(
        default=0,
        ge=0,
        description="Reward points for completing the task"
    )

    class Config:
        from_attributes = True

    @classmethod
    @field_validator("due_date")
    def validate_due_date(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("due_date must include timezone information")
            if value < datetime.now(UTC):
                raise ValueError("due_date cannot be in the past")
        return value


class TaskCreateSchema(TaskBaseSchema):
    """Schema for creating a new task."""
    assigned_user_id: Optional[int] = Field(
        ..., gt=0, description="ID of the user to assign; null for unassigned",
    )
    assigned_by_user_id: int = Field(
        ..., gt=0, description="ID of the user who assigns the task",
    )


class TaskUpdateSchema(BaseModel):
    """Schema for updating task information."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_completed: Optional[bool] = None
    assigned_user_id: Optional[int] = Field(None, gt=0)
    assigned_by_user_id: Optional[int] = Field(None, gt=0)
    reward_points: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True

    @classmethod
    @field_validator("due_date")
    def validate_due_date(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("due_date must include timezone information")
            if value < datetime.now(UTC):
                raise ValueError("due_date cannot be in the past")
        return value


class TaskResponseSchema(TaskBaseSchema):
    """Schema for task response with additional fields."""
    id: int = Field(gt=0, description="Task unique identifier")
    is_completed: bool = Field(
        default=False,
        description="Indicates if the task is completed",
    )
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    assigned_user_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID of the user assigned to this task",
    )
    assigned_by_user_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID of the user who assigned this task",
    )


class TaskAssignGroupsSchema(BaseModel):
    """Schema for assigning task to groups."""
    group_ids: Annotated[List[int], Field(min_length=1)]

    model_config = ConfigDict(frozen=True)


class TaskAssignUserSchema(BaseModel):
    """Schema for assigning a task to a user."""
    assigned_by_user_id: int = Field(gt=0)

    model_config = ConfigDict(frozen=True)

