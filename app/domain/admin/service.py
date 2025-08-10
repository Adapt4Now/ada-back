from typing import List
import logging

from app.domain.users.models import UserRole
from app.domain.users.schemas import UserAdminResponseSchema, UserUpdateSchema
from app.database import UnitOfWork

logger = logging.getLogger(__name__)


class AdminService:
    """Service layer for admin-related user operations."""

    def __init__(self, repository_factory, unit_of_work: UnitOfWork):
        self.repository_factory = repository_factory
        self.unit_of_work = unit_of_work

    async def get_users(self) -> List[UserAdminResponseSchema]:
        """Retrieve all users with related data."""
        async with self.unit_of_work as unit_of_work:
            user_repository = self.repository_factory(unit_of_work.session)
            users = await user_repository.get_all_with_relations()
        return [UserAdminResponseSchema.model_validate(u) for u in users]

    async def get_user(self, user_id: int) -> UserAdminResponseSchema:
        """Retrieve a single user with related data."""
        async with self.unit_of_work as unit_of_work:
            user_repository = self.repository_factory(unit_of_work.session)
            user = await user_repository.get_with_relations(user_id)
        return UserAdminResponseSchema.model_validate(user)

    async def make_user_admin(self, user_id: int) -> UserAdminResponseSchema:
        """Promote a user to administrator."""
        logger.info("Promoting user %s to admin", user_id)
        async with self.unit_of_work as unit_of_work:
            user_repository = self.repository_factory(unit_of_work.session)
            user = await user_repository.update(user_id, UserUpdateSchema(role=UserRole.ADMIN))
        logger.info("Promoted user %s to admin", user_id)
        return UserAdminResponseSchema.model_validate(user)
