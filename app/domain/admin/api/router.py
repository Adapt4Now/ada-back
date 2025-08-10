"""Admin endpoints for inspecting full user data."""

from typing import List

from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.domain.users.schemas import UserAdminResponseSchema
from app.core.security import get_current_admin
from app.dependencies import Container
from app.domain.admin.service import AdminService


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)
@router.get("/users", response_model=List[UserAdminResponseSchema])
@inject
async def admin_get_users(
    service: AdminService = Depends(Provide[Container.admin_service]),
) -> List[UserAdminResponseSchema]:
    """Return all users with related data for admin inspection."""
    return await service.get_users()


@router.get("/users/{user_id}", response_model=UserAdminResponseSchema)
@inject
async def admin_get_user(
    user_id: int,
    service: AdminService = Depends(Provide[Container.admin_service]),
) -> UserAdminResponseSchema:
    """Return a single user with all related data."""
    return await service.get_user(user_id)


@router.post("/users/{user_id}/make-admin", response_model=UserAdminResponseSchema)
@inject
async def make_user_admin(
    user_id: int,
    service: AdminService = Depends(Provide[Container.admin_service]),
) -> UserAdminResponseSchema:
    """Grant administrative rights to the specified user."""
    return await service.make_user_admin(user_id)
