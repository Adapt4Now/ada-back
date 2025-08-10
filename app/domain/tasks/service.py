from typing import List
import logging

from .repository import TaskRepository
from .schemas import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
    TaskAssignGroupsSchema,
    TaskAssignUserSchema,
)
from app.database import UnitOfWork

logger = logging.getLogger(__name__)


class TaskService:
    """Service layer for task-related operations."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_tasks(self, include_archived: bool = False) -> List[TaskResponseSchema]:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            tasks = await repo.get_all(include_archived)
        return tasks

    async def create_task(self, task_data: TaskCreateSchema) -> TaskResponseSchema:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            task = await repo.create(task_data)
            await uow.commit()
        return task

    async def get_task_by_id(
        self, task_id: int, include_archived: bool = False
    ) -> TaskResponseSchema:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            task = await repo.get_by_id(task_id, include_archived)
        return task

    async def update_task(
        self, task_id: int, task_data: TaskUpdateSchema
    ) -> TaskResponseSchema:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            task = await repo.update(task_id, task_data)
            await uow.commit()
        return task

    async def delete_task(self, task_id: int) -> None:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            await repo.delete(task_id)
            await uow.commit()

    async def assign_task_to_user(
        self, task_id: int, user_id: int, assignment: TaskAssignUserSchema
    ) -> TaskResponseSchema:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            task = await repo.assign_to_user(
                task_id, user_id, assignment.assigned_by_user_id
            )
            await uow.commit()
        return task

    async def unassign_task_from_user(
        self, task_id: int, user_id: int
    ) -> TaskResponseSchema:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            task = await repo.unassign_from_user(task_id, user_id)
            await uow.commit()
        return task

    async def assign_task_to_groups(
        self, task_id: int, assignment: TaskAssignGroupsSchema
    ) -> TaskResponseSchema:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            task = await repo.assign_to_groups(task_id, list(assignment.group_ids))
            await uow.commit()
        return task

    async def unassign_task_from_group(
        self, task_id: int, group_id: int
    ) -> TaskResponseSchema:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            task = await repo.unassign_from_group(task_id, group_id)
            await uow.commit()
        return task

    async def restore_task(self, task_id: int) -> TaskResponseSchema:
        async with self.uow as uow:
            repo = TaskRepository(uow.session)
            task = await repo.restore(task_id)
            await uow.commit()
        return task
