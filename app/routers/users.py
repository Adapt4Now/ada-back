from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import get_users as crud_get_users
from app.database import get_database_session
from app.schemas.user import (
    UserResponseSchema,
    UserCreateSchema,
    UserUpdateSchema
)

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
) -> dict:
    """
    Create a new user with the provided data:
    - **username**: required
    - **email**: required
    - **password**: required
    """
    return {"message": "create_user endpoint"}


@router.get(
    "/",
    response_model=List[UserResponseSchema],
    summary="Get all users"
)
async def get_users_list(
        db: AsyncSession = Depends(get_database_session)
) -> List[dict]:
    """
    Retrieve all users from the system.
    """
    return await crud_get_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Get user by ID"
)
async def get_user_details(
        user_id: int,
        db: AsyncSession = Depends(get_database_session)
) -> dict:
    """
    Get detailed information about a specific user.

    Parameters:
    - **user_id**: unique identifier of the user
    """
    return {"message": "get_user_by_id endpoint"}


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
    return None


@router.put(
    "/{user_id}",
    response_model=UserResponseSchema,
    summary="Update user"
)
async def update_user(
        user_id: int,
        user_data: UserUpdateSchema,
        db: AsyncSession = Depends(get_database_session)
) -> dict:
    """
    Update user information.

    Parameters:
    - **user_id**: unique identifier of the user to update
    - **user_data**: updated user information
    """
    return {"message": "update_user endpoint"}
