from app.domain.settings.schemas import SettingResponse, SettingUpdate
from app.database import UnitOfWork
import logging

logger = logging.getLogger(__name__)


class SettingService:
    """Service layer for user settings operations."""

    def __init__(self, repository_factory, unit_of_work: UnitOfWork):
        self.repository_factory = repository_factory
        self.unit_of_work = unit_of_work

    async def get_settings(self, user_id: int) -> SettingResponse:
        """Retrieve settings for a user."""
        async with self.unit_of_work as unit_of_work:
            setting_repository = self.repository_factory(unit_of_work.session)
            setting = await setting_repository.get_or_create(user_id)
        return SettingResponse.model_validate(setting)

    async def update_settings(
        self, user_id: int, data: SettingUpdate
    ) -> SettingResponse:
        """Update user settings."""
        logger.info("Updating settings for user %s", user_id)
        async with self.unit_of_work as unit_of_work:
            setting_repository = self.repository_factory(unit_of_work.session)
            setting = await setting_repository.update(user_id, data)
        logger.info("Updated settings for user %s", user_id)
        return SettingResponse.model_validate(setting)
