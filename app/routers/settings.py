from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.crud.setting import SettingRepository
from app.schemas.setting import SettingResponse, SettingUpdate

router = APIRouter()


def get_setting_repository(
    db: AsyncSession = Depends(get_database_session),
) -> SettingRepository:
    return SettingRepository(db)


@router.get("/settings/{user_id}", response_model=SettingResponse)
async def get_settings(
    user_id: int,
    repo: SettingRepository = Depends(get_setting_repository),
):
    setting = await repo.get_or_create(user_id)
    return SettingResponse.model_validate(setting)


@router.put("/settings/{user_id}", response_model=SettingResponse)
async def update_settings_endpoint(
    user_id: int,
    data: SettingUpdate,
    repo: SettingRepository = Depends(get_setting_repository),
):
    setting = await repo.update(user_id, data)
    return SettingResponse.model_validate(setting)
