from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.setting import Setting
from app.schemas.setting import SettingUpdate


async def get_or_create_settings(db: AsyncSession, user_id: int) -> Setting:
    result = await db.execute(select(Setting).where(Setting.user_id == user_id))
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = Setting(user_id=user_id)
        db.add(setting)
        await db.commit()
        await db.refresh(setting)
    return setting


async def update_settings(db: AsyncSession, user_id: int, data: SettingUpdate) -> Setting:
    setting = await get_or_create_settings(db, user_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(setting, field, value)
    await db.commit()
    await db.refresh(setting)
    return setting
