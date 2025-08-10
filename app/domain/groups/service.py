from typing import List
import logging

from app.core.exceptions import GroupNotFoundError
from .schemas import GroupCreate, GroupUpdate, GroupResponse
from app.database import UnitOfWork

logger = logging.getLogger(__name__)


class GroupService:
    """Service layer for group-related operations."""

    def __init__(self, repository_factory, unit_of_work: UnitOfWork):
        self.repository_factory = repository_factory
        self.unit_of_work = unit_of_work

    async def get_groups(self) -> List[GroupResponse]:
        """Retrieve all groups."""
        async with self.unit_of_work as unit_of_work:
            group_repository = self.repository_factory(unit_of_work.session)
            groups = await group_repository.get_list()
        return [GroupResponse.model_validate(group) for group in groups]

    async def create_group(self, group_data: GroupCreate) -> GroupResponse:
        """Create a new group."""
        logger.info("Creating group")
        async with self.unit_of_work as unit_of_work:
            group_repository = self.repository_factory(unit_of_work.session)
            new_group = await group_repository.create(group_data)
        logger.info("Created group %s", new_group.id)
        return GroupResponse.model_validate(new_group)

    async def delete_group(self, group_id: int) -> None:
        """Delete a group."""
        logger.info("Deleting group %s", group_id)
        async with self.unit_of_work as unit_of_work:
            group_repository = self.repository_factory(unit_of_work.session)
            group = await group_repository.delete(group_id)
        if group is None:
            raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
        logger.info("Deleted group %s", group_id)

    async def update_group(self, group_id: int, group_data: GroupUpdate) -> GroupResponse:
        """Update group information."""
        logger.info("Updating group %s", group_id)
        async with self.unit_of_work as unit_of_work:
            group_repository = self.repository_factory(unit_of_work.session)
            group = await group_repository.update(group_id, group_data)
        if group is None:
            raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
        logger.info("Updated group %s", group_id)
        return GroupResponse.model_validate(group)

    async def add_user_to_group(self, group_id: int, user_id: int) -> GroupResponse:
        """Add a user to a group."""
        logger.info("Adding user %s to group %s", user_id, group_id)
        async with self.unit_of_work as unit_of_work:
            group_repository = self.repository_factory(unit_of_work.session)
            group = await group_repository.get(group_id, active_only=False)
            if group is None:
                raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
            updated_group = await group_repository.add_users(group_id, {user_id: "member"})
        if updated_group is None:
            raise GroupNotFoundError("Failed to update group membership")
        logger.info("Added user %s to group %s", user_id, group_id)
        return GroupResponse.model_validate(updated_group)

    async def remove_user_from_group(self, group_id: int, user_id: int) -> GroupResponse:
        """Remove a user from a group."""
        logger.info("Removing user %s from group %s", user_id, group_id)
        async with self.unit_of_work as unit_of_work:
            group_repository = self.repository_factory(unit_of_work.session)
            group = await group_repository.get(group_id, active_only=False)
            if group is None:
                raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
            updated_group = await group_repository.remove_users(group_id, [user_id])
        if updated_group is None:
            raise GroupNotFoundError("Failed to update group membership")
        logger.info("Removed user %s from group %s", user_id, group_id)
        return GroupResponse.model_validate(updated_group)
