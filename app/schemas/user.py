from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

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

    model_config = ConfigDict(
        str_strip_whitespace=True,
        frozen=True
    )


class UserResponseSchema(UserSchemaBase):
    """Schema for user data response."""
    id: Annotated[int, Field(gt=0)]
    is_active: bool = Field(default=True)

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True
    )
