from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.models.group import Group
from app.models.user import User
from app.schemas.task import TaskCreateSchema, TaskResponseSchema, TaskUpdateSchema
from app.crud.achievement import AchievementRepository
from app.core.exceptions import TaskNotFoundError

UTC = ZoneInfo("UTC")


class TaskRepository:
    """Repository for managing task operations in the database."""

    def __init__(self, db: AsyncSession):
        self.db = db

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
            status=task_data.status,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        if db_task.status == TaskStatus.COMPLETED:
            db_task.completed_at = datetime.now(UTC)
        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        return self._to_task_details(db_task)

    async def get_by_id(self, task_id: int) -> TaskResponseSchema:
        """Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task details

        Raises:
            TaskNotFoundError: If the task does not exist
        """
        query = select(Task).where(
            Task.id == task_id, Task.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        task = result.scalars().first()
        if task is None:
            raise TaskNotFoundError
        return self._to_task_details(task)

    async def get_all(self) -> List[TaskResponseSchema]:
        """
        Get all tasks.

        Returns:
            List of task details
        """
        query = select(Task).where(Task.deleted_at.is_(None))
        result = await self.db.execute(query)
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
        result = await self.db.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        task = result.scalars().first()

        if not task:
            raise TaskNotFoundError

        update_data = task_data.model_dump(exclude_unset=True)

        was_completed = task.is_completed

        for key, value in update_data.items():
            setattr(task, key, value)

        task.updated_at = datetime.now(UTC)
        status = update_data.get('status')
        if status is not None:
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now(UTC)
            else:
                task.completed_at = None

        await self.db.commit()
        if update_data.get('is_completed') and task.assigned_user_id:
            await AchievementRepository(self.db).check_task_completion_achievements(
                task.assigned_user_id
            )
        await self.db.refresh(task)
        return self._to_task_details(task)

    async def delete(self, task_id: int) -> None:
        """Delete task by ID.

        Args:
            task_id: Task identifier

        Raises:
            TaskNotFoundError: If the task doesn't exist
        """
        result = await self.db.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        task = result.scalars().first()
        if not task:
            raise TaskNotFoundError
        task.deleted_at = datetime.now(UTC)
        task.is_archived = True
        await self.db.commit()

    async def restore(self, task_id: int) -> TaskResponseSchema:
        """Restore an archived task by ID."""
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        task = result.scalars().first()
        if not task or task.deleted_at is None:
            raise TaskNotFoundError(detail="Task not found or not archived")
        task.deleted_at = None
        task.is_archived = False
        await self.db.commit()
        await self.db.refresh(task)
        return self._to_task_details(task)

    async def assign_to_user(self, task_id: int, user_id: int) -> TaskResponseSchema:
        """
        Assign task to user.

        Args:
            task_id: Task identifier
            user_id: User identifier

        Returns:
            Updated task details

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        update_data = TaskUpdateSchema(**{"assigned_user_id": user_id})
        return await self.update(task_id, update_data)

    async def assign_to_groups(self, task_id: int, group_ids: List[int]) -> TaskResponseSchema:
        """
        Assign a task to groups.

        Args:
            task_id: Task identifier
            group_ids: List of group identifiers

        Returns:
            Updated task details

        Raises:
            TaskNotFoundError: If a task with a given ID doesn't exist
        """
        result = await self.db.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        task = result.scalars().first()

        if not task:
            raise TaskNotFoundError

        groups_result = await self.db.execute(
            select(Group).where(Group.id.in_(group_ids))
        )
        groups = list(groups_result.scalars().all())

        task.assigned_groups = groups
        task.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(task)
        return self._to_task_details(task)
