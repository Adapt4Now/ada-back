from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.base import BaseRepository
from .models import Task, TaskStatus
from app.domain.groups.models import Group
from app.domain.users.models import User
from .schemas import TaskCreateSchema, TaskResponseSchema, TaskUpdateSchema
from app.domain.achievements.repository import AchievementRepository
from app.core.exceptions import AppError, TaskNotFoundError, GroupNotFoundError

UTC = ZoneInfo("UTC")


class TaskRepository(BaseRepository[Task]):
    """Repository for managing task operations in the database."""

    model = Task

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_task_details(task: Task) -> TaskResponseSchema:
        """
        Convert Task model to TaskResponseSchema schema.

        Args:
            task: Task model instance

        Returns:
            TaskResponseSchema schema instance
        """
        return TaskResponseSchema.model_validate(task)

    async def create(self, task_data: TaskCreateSchema) -> TaskResponseSchema:
        """
        Create a new task.

        Args:
            task_data: Task creation data

        Returns:
            Created task details
        """
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            reward_points=task_data.reward_points,
            due_date=task_data.due_date,
            assigned_user_id=task_data.assigned_user_id,
            assigned_by_user_id=task_data.assigned_by_user_id,
            status=task_data.status,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        if db_task.status == TaskStatus.COMPLETED:
            db_task.completed_at = datetime.now(UTC)
        self.session.add(db_task)
        await self.session.flush()
        return self._to_task_details(db_task)

    async def get_by_id(self, task_id: int, include_archived: bool = False) -> TaskResponseSchema:
        """Get a task by ID.

        Args:
            task_id: Task identifier
            include_archived: Include archived tasks if True

        Returns:
            Task details

        Raises:
            TaskNotFoundError: If the task does not exist
        """
        query = select(Task).where(Task.id == task_id)
        if not include_archived:
            query = query.where(Task.deleted_at.is_(None))
        result = await self.session.execute(query)
        task = result.scalars().first()
        if task is None:
            raise TaskNotFoundError
        return self._to_task_details(task)

    async def get_all(self, include_archived: bool = False) -> List[TaskResponseSchema]:
        """
        Get all tasks.

        Args:
            include_archived: Include archived tasks if True

        Returns:
            List of task details
        """
        query = select(Task)
        if not include_archived:
            query = query.where(Task.deleted_at.is_(None))
        result = await self.session.execute(query)
        tasks = list(result.scalars().all())
        return [self._to_task_details(task) for task in tasks]

    async def update(self, task_id: int, task_data: TaskUpdateSchema) -> TaskResponseSchema:
        """
        Update task by ID.

        Args:
            task_id: Task identifier
            task_data: Task update data

        Returns:
            Updated task details

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        task = result.scalars().first()

        if not task:
            raise TaskNotFoundError

        update_data = task_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(task, key, value)

        task.updated_at = datetime.now(UTC)
        status = update_data.get('status')
        if status is not None:
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now(UTC)
            else:
                task.completed_at = None

        if status == TaskStatus.COMPLETED and task.assigned_user_id:
            await AchievementRepository(self.session).check_task_completion_achievements(
                task.assigned_user_id
            )

        return self._to_task_details(task)

    async def delete(self, task_id: int) -> None:
        """Delete task by ID.

        Args:
            task_id: Task identifier

        Raises:
            TaskNotFoundError: If the task doesn't exist
        """
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        task = result.scalars().first()
        if not task:
            raise TaskNotFoundError
        task.deleted_at = datetime.now(UTC)
        task.is_archived = True

    async def restore(self, task_id: int) -> TaskResponseSchema:
        """Restore an archived task by ID."""
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        task = result.scalars().first()
        if not task or task.deleted_at is None:
            raise TaskNotFoundError(detail="Task not found or not archived")
        task.deleted_at = None
        task.is_archived = False
        return self._to_task_details(task)

    async def assign_to_user(
        self, task_id: int, user_id: int, assigned_by_user_id: int
    ) -> TaskResponseSchema:
        """
        Assign task to user.

        Args:
            task_id: Task identifier
            user_id: User identifier
            assigned_by_user_id: ID of the user who assigns the task

        Returns:
            Updated task details

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        update_data = TaskUpdateSchema(
            assigned_user_id=user_id, assigned_by_user_id=assigned_by_user_id
        )
        return await self.update(task_id, update_data)

    async def assign_to_groups(self, task_id: int, group_ids: List[int]) -> TaskResponseSchema:
        """Assign a task to groups."""
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        task = result.scalars().first()

        if not task:
            raise TaskNotFoundError

        groups_result = await self.session.execute(
            select(Group).where(Group.id.in_(group_ids))
        )
        groups = list(groups_result.scalars().all())

        if len(groups) != len(group_ids):
            raise GroupNotFoundError("One or more groups not found")

        task.assigned_groups = groups
        task.updated_at = datetime.now(UTC)

        return self._to_task_details(task)

    async def unassign_from_user(
        self, task_id: int, user_id: int
    ) -> TaskResponseSchema:
        """Remove task assignment from a user."""
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        task = result.scalars().first()

        if not task:
            raise TaskNotFoundError

        if task.assigned_user_id != user_id:
            raise AppError("Task is not assigned to this user")

        task.assigned_user_id = None
        task.assigned_by_user_id = None
        task.updated_at = datetime.now(UTC)
        return self._to_task_details(task)

    async def unassign_from_group(
        self, task_id: int, group_id: int
    ) -> TaskResponseSchema:
        """Remove task assignment from a group."""
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        task = result.scalars().first()

        if not task:
            raise TaskNotFoundError

        group_result = await self.session.execute(select(Group).where(Group.id == group_id))
        group = group_result.scalar_one_or_none()

        if group is None or group not in task.assigned_groups:
            raise AppError("Task is not assigned to this group")

        task.assigned_groups.remove(group)
        task.updated_at = datetime.now(UTC)
        return self._to_task_details(task)
