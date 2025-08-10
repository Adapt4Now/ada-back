from app.domain.settings.repository import SettingRepository
from app.domain.settings.schemas import SettingResponse, SettingUpdate
from app.database import UnitOfWork


class SettingService:
    """Service layer for user settings operations."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_settings(self, user_id: int) -> SettingResponse:
        async with self.uow as uow:
            repo = SettingRepository(uow.session)
            setting = await repo.get_or_create(user_id)
        return SettingResponse.model_validate(setting)

    async def update_settings(
        self, user_id: int, data: SettingUpdate
    ) -> SettingResponse:
        async with self.uow as uow:
            repo = SettingRepository(uow.session)
            setting = await repo.update(user_id, data)
        return SettingResponse.model_validate(setting)
