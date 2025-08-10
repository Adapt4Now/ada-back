from typing import List
import logging

from app.domain.users.models import UserRole
from app.domain.users.schemas import UserAdminResponseSchema, UserUpdateSchema
from app.domain.users.repository import UserRepository

logger = logging.getLogger(__name__)


class AdminService:
    """Service layer for admin-related user operations."""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_users(self) -> List[UserAdminResponseSchema]:
        users = await self.repo.get_all_with_relations()
        return [UserAdminResponseSchema.model_validate(u) for u in users]

    async def get_user(self, user_id: int) -> UserAdminResponseSchema:
        user = await self.repo.get_with_relations(user_id)
        return UserAdminResponseSchema.model_validate(user)

    async def make_user_admin(self, user_id: int) -> UserAdminResponseSchema:
        user = await self.repo.update(user_id, UserUpdateSchema(role=UserRole.ADMIN))
        return UserAdminResponseSchema.model_validate(user)
