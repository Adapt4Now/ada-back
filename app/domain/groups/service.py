from typing import List

from app.core.exceptions import GroupNotFoundError
from .schemas import GroupCreate, GroupUpdate, GroupResponse
from app.database import UnitOfWork


class GroupService:
    """Service layer for group-related operations."""

    def __init__(self, repo_factory, uow: UnitOfWork):
        self.repo_factory = repo_factory
        self.uow = uow

    async def get_groups(self) -> List[GroupResponse]:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            groups = await repo.get_list()
        return [GroupResponse.model_validate(group) for group in groups]

    async def create_group(self, group_data: GroupCreate) -> GroupResponse:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            new_group = await repo.create(group_data)
        return GroupResponse.model_validate(new_group)

    async def delete_group(self, group_id: int) -> None:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            group = await repo.delete(group_id)
        if group is None:
            raise GroupNotFoundError(detail=f"Group with id {group_id} not found")

    async def update_group(self, group_id: int, group_data: GroupUpdate) -> GroupResponse:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            group = await repo.update(group_id, group_data)
        if group is None:
            raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
        return GroupResponse.model_validate(group)

    async def add_user_to_group(self, group_id: int, user_id: int) -> GroupResponse:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            group = await repo.get(group_id, active_only=False)
            if group is None:
                raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
            updated_group = await repo.add_users(group_id, {user_id: "member"})
        assert updated_group is not None
        return GroupResponse.model_validate(updated_group)

    async def remove_user_from_group(self, group_id: int, user_id: int) -> GroupResponse:
        async with self.uow as uow:
            repo = self.repo_factory(uow.session)
            group = await repo.get(group_id, active_only=False)
            if group is None:
                raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
            updated_group = await repo.remove_users(group_id, [user_id])
        assert updated_group is not None
        return GroupResponse.model_validate(updated_group)
