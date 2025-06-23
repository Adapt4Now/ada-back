"""Admin endpoints for inspecting full user data."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.models.user import User
from app.schemas.user import UserAdminResponseSchema


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserAdminResponseSchema])
async def admin_get_users(db: AsyncSession = Depends(get_database_session)) -> List[UserAdminResponseSchema]:
    """Return all users with related data for admin inspection."""
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.family),
            selectinload(User.groups),
            selectinload(User.tasks),
            selectinload(User.notifications),
            selectinload(User.settings),
        )
    )
    users = result.scalars().all()
    return [UserAdminResponseSchema.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserAdminResponseSchema)
async def admin_get_user(user_id: int, db: AsyncSession = Depends(get_database_session)) -> UserAdminResponseSchema:
    """Return a single user with all related data."""
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.family),
            selectinload(User.groups),
            selectinload(User.tasks),
            selectinload(User.notifications),
            selectinload(User.settings),
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserAdminResponseSchema.model_validate(user)
