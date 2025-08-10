from typing import List
import logging

from .repository import UserRepository
from .schemas import (
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)
from .models import UserStatus

logger = logging.getLogger(__name__)


class UserService:
    """Service layer for user-related operations."""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        new_user = await self.repo.create(user_data)
        logger.info("Created user %s", new_user.id)
        return UserResponseSchema.model_validate(new_user)

    async def get_users(self) -> List[UserResponseSchema]:
        users = await self.repo.get_all()
        return [UserResponseSchema.model_validate(user) for user in users]

    async def get_user(self, user_id: int) -> UserResponseSchema:
        user = await self.repo.get_by_id(user_id)
        return UserResponseSchema.model_validate(user)

    async def delete_user(self, user_id: int) -> None:
        await self.repo.delete(user_id)
        logger.info("Deleted user %s", user_id)

    async def update_user(
        self, user_id: int, user_data: UserUpdateSchema
    ) -> UserResponseSchema:
        user = await self.repo.update(user_id, user_data)
        return UserResponseSchema.model_validate(user)

    async def update_status(
        self, user_id: int, status: UserStatus
    ) -> UserResponseSchema:
        user = await self.repo.update_status(user_id, status)
        return UserResponseSchema.model_validate(user)
