from app.crud.setting import SettingRepository
from app.schemas.setting import SettingResponse, SettingUpdate


class SettingService:
    """Service layer for user settings operations."""

    def __init__(self, repo: SettingRepository):
        self.repo = repo

    async def get_settings(self, user_id: int) -> SettingResponse:
        setting = await self.repo.get_or_create(user_id)
        return SettingResponse.model_validate(setting)

    async def update_settings(
        self, user_id: int, data: SettingUpdate
    ) -> SettingResponse:
        setting = await self.repo.update(user_id, data)
        return SettingResponse.model_validate(setting)
