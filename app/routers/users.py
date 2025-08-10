from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.crud.user import (
    get_users as crud_get_users,
    create_user as crud_create_user,
    get_user as crud_get_user,
    update_user as crud_update_user,
    delete_user as crud_delete_user,
    update_user_status as crud_update_user_status,
)
from app.database import get_database_session
from app.schemas.user import (
    UserResponseSchema,
    UserCreateSchema,
    UserUpdateSchema
)
from app.models.user import UserStatus

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post(
    "/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user"
)
async def create_user(
        user_data: UserCreateSchema,
        db: AsyncSession = Depends(get_database_session)
) -> UserResponseSchema:
    """
    Create a new user with the provided data:
    - **username**: required
    - **email**: required
    - **password**: required
    """
    new_user = await crud_create_user(db, user_data)
    return UserResponseSchema.model_validate(new_user)


@router.get(
    "/",
    response_model=List[UserResponseSchema],
    summary="Get all users"
)
async def get_users_list(
        db: AsyncSession = Depends(get_database_session)
) -> List[UserResponseSchema]:
    """
    Retrieve all users from the system.
    """
    users = await crud_get_users(db)
    return [UserResponseSchema.model_validate(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Get user by ID"
)
async def get_user_details(
        user_id: int,
        db: AsyncSession = Depends(get_database_session)
) -> UserResponseSchema:
    """
    Get detailed information about a specific user.

    Parameters:
    - **user_id**: unique identifier of the user
    """
    user = await crud_get_user(db, user_id)
    return UserResponseSchema.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user"
)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_database_session)
) -> None:
    """
    Delete a user from the system.

    Parameters:
    - **user_id**: unique identifier of the user to delete
    """
    await crud_delete_user(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Update user"
)
async def update_user(
        user_id: int,
        user_data: UserUpdateSchema,
        db: AsyncSession = Depends(get_database_session)
) -> UserResponseSchema:
    """
    Update user information.

    Parameters:
    - **user_id**: unique identifier of the user to update
    - **user_data**: updated user information
    """
    user = await crud_update_user(db, user_id, user_data)
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
    db: AsyncSession = Depends(get_database_session),
) -> UserResponseSchema:
    """Update the status of a user."""
    user = await crud_update_user_status(db, user_id, status_data.status)
    return UserResponseSchema.model_validate(user)
