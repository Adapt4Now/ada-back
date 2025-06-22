from typing import Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime, UTC


class GroupBase(BaseModel):
    """Base schema for a group, defining common attributes."""
    name: Annotated[str, Field(
        min_length=1, 
        max_length=100, 
        description="Group name",
        examples=["Administrators", "Users"]
    )]
    description: Optional[str] = Field(
        None, 
        description="Optional group description",
        examples=["Group for system administrators", "Regular users group"]
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
        json_schema_extra={
            "example": {
                "name": "Example Group",
                "description": "This is an example group"
            }
        }
    )

    @classmethod
    @model_validator(mode='before')
    def validate_group_data(cls, values: dict) -> dict:
        """Validate group data before model creation."""
        if isinstance(values, dict):
            if 'name' in values:
                name = values['name']
                if not isinstance(name, str) or not name.strip():
                    raise ValueError("Group name cannot be empty or contain only whitespace")
                if any(char in name for char in ['<', '>', '&', '"', "'"]):
                    raise ValueError("Group name contains invalid characters")
                values['name'] = name.strip()
        return values


class GroupCreate(GroupBase):
    """Schema for creating a new group."""
    created_by: Annotated[str, Field(
        min_length=1,
        max_length=100,
        description="Username of group creator",
        examples=["admin", "system"]
    )]
    is_active: bool = Field(
        default=True,
        description="Flag indicating if the group is active"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of group creation"
    )

    @classmethod
    @field_validator('created_by')
    def validate_created_by(cls, value: str) -> str:
        """Validate creator username."""
        if not value.strip():
            raise ValueError("Creator username cannot be empty")
        return value.strip()

    @model_validator(mode='after')
    def validate_timestamps(self) -> 'GroupCreate':
        """Validate timestamps after model creation."""
        if self.created_at > datetime.now(UTC):
            raise ValueError("Creation time cannot be in the future")
        return self


class GroupUpdate(BaseModel):
    """Schema for updating an existing group."""
    name: Optional[Annotated[str, Field(
        min_length=1, 
        max_length=100, 
        description="Group name"
    )]] = None
    description: Optional[str] = Field(
        None, 
        description="Optional group description"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Flag indicating if the group is active"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of last update"
    )

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True
    )

    @classmethod
    @field_validator('name')
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        """Validate group name if provided."""
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Group name cannot be empty or contain only whitespace")
        if any(char in value for char in ['<', '>', '&', '"', "'"]):
            raise ValueError("Group name contains invalid characters")
        return value

    @model_validator(mode='after')
    def validate_update_data(self) -> 'GroupUpdate':
        """Validate update data after model creation."""
        if not any([self.name, self.description, self.is_active is not None]):
            raise ValueError("At least one field must be provided for update")
        if self.updated_at > datetime.now(UTC):
            raise ValueError("Update time cannot be in the future")
        return self


class GroupResponse(GroupBase):
    """Schema for group data response."""
    id: Annotated[int, Field(
        gt=0, 
        description="Unique group identifier",
        examples=[1, 42]
    )]
    created_by: str = Field(
        description="Username of group creator"
    )
    created_at: datetime = Field(
        description="Timestamp of group creation"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp of last update"
    )
    is_active: bool = Field(
        description="Flag indicating if the group is active"
    )

    @model_validator(mode='after')
    def validate_timestamps(self) -> 'GroupResponse':
        """Validate response timestamps."""
        if self.updated_at and self.updated_at < self.created_at:
            raise ValueError("Update time cannot be earlier than creation time")
        return self