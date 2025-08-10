from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends

from app.domain.settings.schemas import SettingResponse, SettingUpdate
from app.domain.settings.service import SettingService
from app.dependencies import container

router = APIRouter()


@router.get("/settings/{user_id}", response_model=SettingResponse)
async def get_settings(
    user_id: int,
    service: SettingService = Depends(container.setting_service),
):
    return await service.get_settings(user_id)


@router.put("/settings/{user_id}", response_model=SettingResponse)
async def update_settings_endpoint(
    user_id: int,
    data: SettingUpdate,
    service: SettingService = Depends(container.setting_service),
):
    return await service.update_settings(user_id, data)
