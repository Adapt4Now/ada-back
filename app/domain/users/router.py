from typing import List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.dependencies import get_user_service
from .schemas import (
    UserResponseSchema,
    UserCreateSchema,
    UserUpdateSchema,
)
from .models import UserStatus
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
)
async def create_user(
    user_data: UserCreateSchema,
    service: UserService = Depends(get_user_service),
) -> UserResponseSchema:
    """Create a new user."""
    return await service.create_user(user_data)


@router.get(
    "/",
    response_model=List[UserResponseSchema],
    summary="Get all users",
)
async def get_users_list(
    service: UserService = Depends(get_user_service),
) -> List[UserResponseSchema]:
    """Retrieve all users from the system."""
    return await service.get_users()


@router.get(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Get user by ID",
)
async def get_user_details(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponseSchema:
    """Get detailed information about a specific user."""
    return await service.get_user(user_id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> None:
    """Delete a user from the system."""
    await service.delete_user(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Update user",
)
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    service: UserService = Depends(get_user_service),
) -> UserResponseSchema:
    """Update user information."""
    return await service.update_user(user_id, user_data)


class UserStatusUpdate(BaseModel):
    status: UserStatus


@router.put(
    "/{user_id}/status",
    response_model=UserResponseSchema,
    summary="Update user status",
)
async def update_user_status_endpoint(
    user_id: int,
    status_data: UserStatusUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponseSchema:
    """Update the status of a user."""
    return await service.update_status(user_id, status_data.status)
