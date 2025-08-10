from typing import List
import logging

from app.database import UnitOfWork
from .schemas import (
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)
from .models import UserStatus

logger = logging.getLogger(__name__)


class UserService:
    """Service layer for user-related operations."""

    def __init__(self, repository_factory, unit_of_work: UnitOfWork):
        self.repository_factory = repository_factory
        self.unit_of_work = unit_of_work

    async def create_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        """Create a new user."""
        logger.info("Creating user")
        async with self.unit_of_work as unit_of_work:
            user_repository = self.repository_factory(unit_of_work.session)
            new_user = await user_repository.create(user_data)
        logger.info("Created user %s", new_user.id)
        return UserResponseSchema.model_validate(new_user)

    async def get_users(self) -> List[UserResponseSchema]:
        """Retrieve all users."""
        async with self.unit_of_work as unit_of_work:
            user_repository = self.repository_factory(unit_of_work.session)
            users = await user_repository.get_all()
        return [UserResponseSchema.model_validate(user) for user in users]

    async def get_user(self, user_id: int) -> UserResponseSchema:
        """Retrieve a user by id."""
        async with self.unit_of_work as unit_of_work:
            user_repository = self.repository_factory(unit_of_work.session)
            user = await user_repository.get_by_id(user_id)
        return UserResponseSchema.model_validate(user)

    async def delete_user(self, user_id: int) -> None:
        """Delete a user by id."""
        logger.info("Deleting user %s", user_id)
        async with self.unit_of_work as unit_of_work:
            user_repository = self.repository_factory(unit_of_work.session)
            await user_repository.delete(user_id)
        logger.info("Deleted user %s", user_id)

    async def update_user(
        self, user_id: int, user_data: UserUpdateSchema
    ) -> UserResponseSchema:
        """Update user information."""
        logger.info("Updating user %s", user_id)
        async with self.unit_of_work as unit_of_work:
            user_repository = self.repository_factory(unit_of_work.session)
            user = await user_repository.update(user_id, user_data)
        logger.info("Updated user %s", user_id)
        return UserResponseSchema.model_validate(user)

    async def update_status(
        self, user_id: int, status: UserStatus
    ) -> UserResponseSchema:
        """Update user status."""
        logger.info("Updating status for user %s", user_id)
        async with self.unit_of_work as unit_of_work:
            user_repository = self.repository_factory(unit_of_work.session)
            user = await user_repository.update_status(user_id, status)
        logger.info("Updated status for user %s", user_id)
        return UserResponseSchema.model_validate(user)
