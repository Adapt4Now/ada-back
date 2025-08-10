from typing import List

from app.core.exceptions import GroupNotFoundError
from app.domain.base import BaseService

from .repository import GroupRepository
from .schemas import GroupCreate, GroupUpdate, GroupResponse


class GroupService(BaseService):
    """Service layer for group-related operations."""

    def __init__(self, repo: GroupRepository):
        super().__init__(repo)
        self.repo = repo

    async def get_groups(self) -> List[GroupResponse]:
        groups = await self.get_list()
        return [GroupResponse.model_validate(group) for group in groups]

    async def create_group(self, group_data: GroupCreate) -> GroupResponse:
        new_group = await self.create(group_data)
        return GroupResponse.model_validate(new_group)

    async def delete_group(self, group_id: int) -> None:
        group = await self.delete(group_id)
        if group is None:
            raise GroupNotFoundError(detail=f"Group with id {group_id} not found")

    async def update_group(self, group_id: int, group_data: GroupUpdate) -> GroupResponse:
        group = await self.update(group_id, group_data)
        if group is None:
            raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
        return GroupResponse.model_validate(group)

    async def add_user_to_group(self, group_id: int, user_id: int) -> GroupResponse:
        group = await self.repo.get(group_id, active_only=False)
        if group is None:
            raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
        updated_group = await self.repo.add_users(group_id, {user_id: "member"})
        assert updated_group is not None
        return GroupResponse.model_validate(updated_group)

    async def remove_user_from_group(self, group_id: int, user_id: int) -> GroupResponse:
        group = await self.repo.get(group_id, active_only=False)
        if group is None:
            raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
        updated_group = await self.repo.remove_users(group_id, [user_id])
        assert updated_group is not None
        return GroupResponse.model_validate(updated_group)
