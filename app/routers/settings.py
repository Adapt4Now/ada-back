from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.crud.setting import get_or_create_settings, update_settings
from app.schemas.setting import SettingResponse, SettingUpdate

router = APIRouter()


@router.get("/settings/{user_id}", response_model=SettingResponse)
async def get_settings(user_id: int, db: AsyncSession = Depends(get_database_session)):
    setting = await get_or_create_settings(db, user_id)
    return SettingResponse.model_validate(setting)


@router.put("/settings/{user_id}", response_model=SettingResponse)
async def update_settings_endpoint(
    user_id: int,
    data: SettingUpdate,
    db: AsyncSession = Depends(get_database_session),
):
    setting = await update_settings(db, user_id, data)
    return SettingResponse.model_validate(setting)
