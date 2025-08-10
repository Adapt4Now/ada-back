from typing import List, Optional

from sqlalchemy import select, insert, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement, user_achievements
from app.models.task import Task
from app.schemas.achievement import (
    AchievementCreateSchema,
    AchievementUpdateSchema,
    AchievementResponseSchema,
)


class AchievementRepository:
    """Repository for managing achievements."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: AchievementCreateSchema) -> AchievementResponseSchema:
        achievement = Achievement(**data.model_dump())
        self.db.add(achievement)
        await self.db.commit()
        await self.db.refresh(achievement)
        return AchievementResponseSchema.model_validate(achievement)

    async def get(self, achievement_id: int) -> Optional[AchievementResponseSchema]:
        result = await self.db.execute(
            select(Achievement).where(Achievement.id == achievement_id)
        )
        achievement = result.scalars().first()
        if achievement is None:
            return None
        return AchievementResponseSchema.model_validate(achievement)

    async def get_all(self) -> List[AchievementResponseSchema]:
        result = await self.db.execute(select(Achievement))
        achievements = result.scalars().all()
        return [AchievementResponseSchema.model_validate(a) for a in achievements]

    async def update(
        self, achievement_id: int, data: AchievementUpdateSchema
    ) -> Optional[AchievementResponseSchema]:
        result = await self.db.execute(
            select(Achievement).where(Achievement.id == achievement_id)
        )
        achievement = result.scalars().first()
        if achievement is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(achievement, field, value)
        await self.db.commit()
        await self.db.refresh(achievement)
        return AchievementResponseSchema.model_validate(achievement)

    async def delete(self, achievement_id: int) -> bool:
        result = await self.db.execute(
            select(Achievement).where(Achievement.id == achievement_id)
        )
        achievement = result.scalars().first()
        if achievement is None:
            return False
        await self.db.delete(achievement)
        await self.db.commit()
        return True

    async def award_to_user(self, achievement_id: int, user_id: int) -> None:
        await self.db.execute(
            insert(user_achievements)
            .values(user_id=user_id, achievement_id=achievement_id)
            .on_conflict_do_nothing()
        )
        await self.db.commit()

    async def get_user_achievements(
        self, user_id: int
    ) -> List[AchievementResponseSchema]:
        result = await self.db.execute(
            select(Achievement)
            .join(user_achievements, Achievement.id == user_achievements.c.achievement_id)
            .where(user_achievements.c.user_id == user_id)
        )
        achievements = result.scalars().all()
        return [AchievementResponseSchema.model_validate(a) for a in achievements]

    async def check_task_completion_achievements(self, user_id: int) -> None:
        """Award achievements for task completion milestones."""
        result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.assigned_user_id == user_id, Task.is_completed.is_(True)
            )
        )
        completed_count = result.scalar_one() or 0
        if completed_count < 1:
            return

        achievement_result = await self.db.execute(
            select(Achievement).where(Achievement.name == "First Task Completed")
        )
        achievement = achievement_result.scalar_one_or_none()
        if not achievement:
            return

        await self.db.execute(
            insert(user_achievements)
            .values(user_id=user_id, achievement_id=achievement.id)
            .on_conflict_do_nothing()
        )
        await self.db.commit()
