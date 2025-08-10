from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.settings.models import Setting
from app.domain.settings.schemas import SettingUpdate


class SettingRepository:
    """Repository for managing user settings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, user_id: int) -> Setting:
        result = await self.db.execute(select(Setting).where(Setting.user_id == user_id))
        setting = result.scalar_one_or_none()
        if setting is None:
            setting = Setting(user_id=user_id, notification_prefs={})
            self.db.add(setting)
            await self.db.commit()
            await self.db.refresh(setting)
        return setting

    async def update(self, user_id: int, data: SettingUpdate) -> Setting:
        setting = await self.get_or_create(user_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(setting, field, value)
        await self.db.commit()
        await self.db.refresh(setting)
        return setting
