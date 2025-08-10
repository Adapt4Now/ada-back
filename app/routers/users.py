from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.crud.user import UserRepository
from app.database import get_database_session
from app.schemas.user import (
    UserResponseSchema,
    UserCreateSchema,
    UserUpdateSchema,
)
from app.models.user import UserStatus

router = APIRouter(prefix="/users", tags=["users"])


def get_user_repository(
    db: AsyncSession = Depends(get_database_session),
) -> UserRepository:
    return UserRepository(db)


@router.post(
    "/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
)
async def create_user(
    user_data: UserCreateSchema,
    repo: UserRepository = Depends(get_user_repository),
) -> UserResponseSchema:
    """Create a new user."""
    new_user = await repo.create(user_data)
    return UserResponseSchema.model_validate(new_user)


@router.get(
    "/",
    response_model=List[UserResponseSchema],
    summary="Get all users",
)
async def get_users_list(
    repo: UserRepository = Depends(get_user_repository),
) -> List[UserResponseSchema]:
    """Retrieve all users from the system."""
    users = await repo.get_all()
    return [UserResponseSchema.model_validate(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Get user by ID",
)
async def get_user_details(
    user_id: int,
    repo: UserRepository = Depends(get_user_repository),
) -> UserResponseSchema:
    """Get detailed information about a specific user."""
    user = await repo.get_by_id(user_id)
    return UserResponseSchema.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
)
async def delete_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repository),
) -> None:
    """Delete a user from the system."""
    await repo.delete(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Update user",
)
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    repo: UserRepository = Depends(get_user_repository),
) -> UserResponseSchema:
    """Update user information."""
    user = await repo.update(user_id, user_data)
    return UserResponseSchema.model_validate(user)


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
    repo: UserRepository = Depends(get_user_repository),
) -> UserResponseSchema:
    """Update the status of a user."""
    user = await repo.update_status(user_id, status_data.status)
    return UserResponseSchema.model_validate(user)
