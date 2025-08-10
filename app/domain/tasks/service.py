from typing import List
import logging

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

    def __init__(self, repository_factory, unit_of_work: UnitOfWork):
        self.repository_factory = repository_factory
        self.unit_of_work = unit_of_work

    async def get_tasks(self, include_archived: bool = False) -> List[TaskResponseSchema]:
        """Retrieve a list of tasks."""
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            tasks = await task_repository.get_all(include_archived)
        return tasks

    async def create_task(self, task_data: TaskCreateSchema) -> TaskResponseSchema:
        """Create a new task."""
        logger.info("Creating task")
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            task = await task_repository.create(task_data)
        logger.info("Created task %s", task.id)
        return task

    async def get_task_by_id(
        self, task_id: int, include_archived: bool = False
    ) -> TaskResponseSchema:
        """Retrieve a task by id."""
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            task = await task_repository.get_by_id(task_id, include_archived)
        return task

    async def update_task(
        self, task_id: int, task_data: TaskUpdateSchema
    ) -> TaskResponseSchema:
        """Update an existing task."""
        logger.info("Updating task %s", task_id)
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            task = await task_repository.update(task_id, task_data)
        logger.info("Updated task %s", task_id)
        return task

    async def delete_task(self, task_id: int) -> None:
        """Delete a task."""
        logger.info("Deleting task %s", task_id)
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            await task_repository.delete(task_id)
        logger.info("Deleted task %s", task_id)

    async def assign_task_to_user(
        self, task_id: int, user_id: int, assignment: TaskAssignUserSchema
    ) -> TaskResponseSchema:
        """Assign a task to a user."""
        logger.info("Assigning task %s to user %s", task_id, user_id)
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            task = await task_repository.assign_to_user(
                task_id, user_id, assignment.assigned_by_user_id
            )
        logger.info("Assigned task %s to user %s", task_id, user_id)
        return task

    async def unassign_task_from_user(
        self, task_id: int, user_id: int
    ) -> TaskResponseSchema:
        """Remove task assignment from a user."""
        logger.info("Unassigning task %s from user %s", task_id, user_id)
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            task = await task_repository.unassign_from_user(task_id, user_id)
        logger.info("Unassigned task %s from user %s", task_id, user_id)
        return task

    async def assign_task_to_groups(
        self, task_id: int, assignment: TaskAssignGroupsSchema
    ) -> TaskResponseSchema:
        """Assign a task to groups."""
        logger.info("Assigning task %s to groups", task_id)
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            task = await task_repository.assign_to_groups(task_id, list(assignment.group_ids))
        logger.info("Assigned task %s to groups", task_id)
        return task

    async def unassign_task_from_group(
        self, task_id: int, group_id: int
    ) -> TaskResponseSchema:
        """Remove a task from a group."""
        logger.info("Unassigning task %s from group %s", task_id, group_id)
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            task = await task_repository.unassign_from_group(task_id, group_id)
        logger.info("Unassigned task %s from group %s", task_id, group_id)
        return task

    async def restore_task(self, task_id: int) -> TaskResponseSchema:
        """Restore a deleted task."""
        logger.info("Restoring task %s", task_id)
        async with self.unit_of_work as unit_of_work:
            task_repository = self.repository_factory(unit_of_work.session)
            task = await task_repository.restore(task_id)
        logger.info("Restored task %s", task_id)
        return task
