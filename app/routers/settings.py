from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.schemas.setting import SettingResponse, SettingUpdate
from app.services import SettingService
from app.crud.setting import SettingRepository

router = APIRouter()


def get_setting_service(
    db: AsyncSession = Depends(get_database_session),
) -> SettingService:
    repo = SettingRepository(db)
    return SettingService(repo)


@router.get("/settings/{user_id}", response_model=SettingResponse)
async def get_settings(
    user_id: int,
    service: SettingService = Depends(get_setting_service),
):
    return await service.get_settings(user_id)


@router.put("/settings/{user_id}", response_model=SettingResponse)
async def update_settings_endpoint(
    user_id: int,
    data: SettingUpdate,
    service: SettingService = Depends(get_setting_service),
):
    return await service.update_settings(user_id, data)
