"""Admin endpoints for inspecting full user data."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.schemas.user import UserAdminResponseSchema
from app.core.security import get_current_admin
from app.services import AdminService
from app.crud.user import UserRepository


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


def get_admin_service(
    db: AsyncSession = Depends(get_database_session),
) -> AdminService:
    repo = UserRepository(db)
    return AdminService(db, repo)


@router.get("/users", response_model=List[UserAdminResponseSchema])
async def admin_get_users(
    service: AdminService = Depends(get_admin_service),
) -> List[UserAdminResponseSchema]:
    """Return all users with related data for admin inspection."""
    return await service.get_users()


@router.get("/users/{user_id}", response_model=UserAdminResponseSchema)
async def admin_get_user(
    user_id: int,
    service: AdminService = Depends(get_admin_service),
) -> UserAdminResponseSchema:
    """Return a single user with all related data."""
    return await service.get_user(user_id)


@router.post("/users/{user_id}/make-admin", response_model=UserAdminResponseSchema)
async def make_user_admin(
    user_id: int,
    service: AdminService = Depends(get_admin_service),
) -> UserAdminResponseSchema:
    """Grant administrative rights to the specified user."""
    return await service.make_user_admin(user_id)
