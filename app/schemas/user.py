from typing import Annotated, Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .family import FamilyResponse
from .group import GroupResponse
from .task import TaskResponseSchema
from .notification import NotificationResponse
from .setting import SettingResponse
from app.models.user import UserRole

# Validation constants
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50
PASSWORD_MIN_LENGTH = 8


class UserSchemaBase(BaseModel):
    """Base schema for user with core fields."""
    username: Annotated[
        str,
        Field(min_length=MIN_USERNAME_LENGTH, max_length=MAX_USERNAME_LENGTH)
    ]
    email: Annotated[
        EmailStr,
        Field(description="User's email in standard format")
    ]

    model_config = ConfigDict(
        str_strip_whitespace=True,
        frozen=True
    )


class UserCreateSchema(UserSchemaBase):
    """Schema for creating a new user."""
    password: Annotated[
        str,
        Field(min_length=PASSWORD_MIN_LENGTH)
    ]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: str = Field(default="en-US")
    timezone: str = Field(default="UTC")
    role: UserRole = Field(default=UserRole.USER)
    points: int = Field(default=0)
    level: Optional[int] = None
    created_by: Optional[int] = None
    family_id: Optional[int] = None


class UserUpdateSchema(BaseModel):
    """Schema for updating user information."""
    username: Optional[Annotated[
        str,
        Field(min_length=MIN_USERNAME_LENGTH, max_length=MAX_USERNAME_LENGTH)
    ]] = None
    email: Optional[Annotated[
        EmailStr,
        Field(description="User's email in standard format")
    ]] = None
    password: Optional[Annotated[
        str,
        Field(min_length=PASSWORD_MIN_LENGTH)
    ]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    role: Optional[UserRole] = None
    last_login_at: Optional[datetime] = None
    points: Optional[int] = None
    level: Optional[int] = None
    created_by: Optional[int] = None
    family_id: Optional[int] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        frozen=True
    )


class UserResponseSchema(UserSchemaBase):
    """Schema for user data response."""
    id: Annotated[int, Field(gt=0)]
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.USER)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: str = Field(default="en-US")
    timezone: str = Field(default="UTC")
    last_login_at: Optional[datetime] = None
    points: int = Field(default=0)
    level: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    family_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True
    )


class UserAdminResponseSchema(UserResponseSchema):
    """Extended user schema for admin endpoints including related data."""

    hashed_password: str
    family: Optional['FamilyResponse'] = None
    groups: List['GroupResponse'] = []
    tasks: List['TaskResponseSchema'] = []
    notifications: List['NotificationResponse'] = []
    settings: Optional['SettingResponse'] = None

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True
    )


