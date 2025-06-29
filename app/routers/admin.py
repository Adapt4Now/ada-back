"""Admin endpoints for inspecting full user data."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, bindparam
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.models.user import User
from app.schemas.user import UserAdminResponseSchema, UserUpdateSchema
from app.core.security import get_current_superuser
from app.crud.user import update_user as crud_update_user


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_superuser)],
)


@router.get("/users", response_model=List[UserAdminResponseSchema])
async def admin_get_users(
    db: AsyncSession = Depends(get_database_session),
) -> List[UserAdminResponseSchema]:
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
async def admin_get_user(
    user_id: int,
    db: AsyncSession = Depends(get_database_session),
) -> UserAdminResponseSchema:
    """Return a single user with all related data."""
    stmt = (
        select(User)
        .where(User.id == bindparam("uid"))
        .options(
            selectinload(User.family),
            selectinload(User.groups),
            selectinload(User.tasks),
            selectinload(User.notifications),
            selectinload(User.settings),
        )
    )
    result = await db.execute(stmt, {"uid": user_id})
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserAdminResponseSchema.model_validate(user)


@router.post("/users/{user_id}/make-admin", response_model=UserAdminResponseSchema)
async def make_user_admin(
    user_id: int,
    db: AsyncSession = Depends(get_database_session),
) -> UserAdminResponseSchema:
    """Grant administrative rights to the specified user."""
    user = await crud_update_user(db, user_id, UserUpdateSchema(is_superuser=True))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserAdminResponseSchema.model_validate(user)
