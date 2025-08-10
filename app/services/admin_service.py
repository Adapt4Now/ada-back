from typing import List

from sqlalchemy import select, bindparam
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserAdminResponseSchema, UserUpdateSchema
from app.crud.user import UserRepository
from app.core.exceptions import UserNotFoundError


class AdminService:
    """Service layer for admin-related user operations."""

    def __init__(self, db: AsyncSession, repo: UserRepository):
        self.db = db
        self.repo = repo

    async def get_users(self) -> List[UserAdminResponseSchema]:
        result = await self.db.execute(
            select(User).options(
                selectinload(User.family),
                selectinload(User.groups),
                selectinload(User.tasks),
                selectinload(User.notifications),
                selectinload(User.settings),
            )
        )
        users = result.scalars().all()
        return [UserAdminResponseSchema.model_validate(u) for u in users]

    async def get_user(self, user_id: int) -> UserAdminResponseSchema:
        stmt = select(User).where(User.id == bindparam("uid")).options(
            selectinload(User.family),
            selectinload(User.groups),
            selectinload(User.tasks),
            selectinload(User.notifications),
            selectinload(User.settings),
        )
        result = await self.db.execute(stmt, {"uid": user_id})
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError()
        return UserAdminResponseSchema.model_validate(user)

    async def make_user_admin(self, user_id: int) -> UserAdminResponseSchema:
        user = await self.repo.update(user_id, UserUpdateSchema(role=UserRole.ADMIN))
        return UserAdminResponseSchema.model_validate(user)
