from typing import List

from app.crud.task import TaskRepository
from app.schemas.task import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
    TaskAssignGroupsSchema,
    TaskAssignUserSchema,
)


class TaskService:
    """Service layer for task-related operations."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    async def get_tasks(self, include_archived: bool = False) -> List[TaskResponseSchema]:
        return await self.repo.get_all(include_archived)

    async def create_task(self, task_data: TaskCreateSchema) -> TaskResponseSchema:
        return await self.repo.create(task_data)

    async def get_task_by_id(
        self, task_id: int, include_archived: bool = False
    ) -> TaskResponseSchema:
        return await self.repo.get_by_id(task_id, include_archived)

    async def update_task(
        self, task_id: int, task_data: TaskUpdateSchema
    ) -> TaskResponseSchema:
        return await self.repo.update(task_id, task_data)

    async def delete_task(self, task_id: int) -> None:
        await self.repo.delete(task_id)

    async def assign_task_to_user(
        self, task_id: int, user_id: int, assignment: TaskAssignUserSchema
    ) -> TaskResponseSchema:
        return await self.repo.assign_to_user(
            task_id, user_id, assignment.assigned_by_user_id
        )

    async def unassign_task_from_user(
        self, task_id: int, user_id: int
    ) -> TaskResponseSchema:
        return await self.repo.unassign_from_user(task_id, user_id)

    async def assign_task_to_groups(
        self, task_id: int, assignment: TaskAssignGroupsSchema
    ) -> TaskResponseSchema:
        return await self.repo.assign_to_groups(task_id, list(assignment.group_ids))

    async def unassign_task_from_group(
        self, task_id: int, group_id: int
    ) -> TaskResponseSchema:
        return await self.repo.unassign_from_group(task_id, group_id)

    async def restore_task(self, task_id: int) -> TaskResponseSchema:
        return await self.repo.restore(task_id)
