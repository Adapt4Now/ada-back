from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.domain.users.repository import UserRepository
from app.domain.users.service import UserService
from app.domain.tasks.repository import TaskRepository
from app.domain.tasks.service import TaskService
from app.domain.admin.service import AdminService
from app.domain.auth.service import AuthService
from app.domain.families.repository import FamilyRepository
from app.domain.families.service import FamilyService
from app.domain.notifications.repository import NotificationRepository
from app.domain.notifications.service import NotificationService
from app.domain.settings.repository import SettingRepository
from app.domain.settings.service import SettingService
from app.domain.groups.repository import GroupRepository
from app.domain.groups.service import GroupService
from app.domain.reports.service import ReportService


def get_session(db: AsyncSession = Depends(get_database_session)) -> AsyncSession:
    return db


def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)


def get_task_repository(session: AsyncSession = Depends(get_session)) -> TaskRepository:
    return TaskRepository(session)


def get_task_service(repo: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(repo)


def get_admin_service(repo: UserRepository = Depends(get_user_repository)) -> AdminService:
    return AdminService(repo)


def get_family_repository(
    session: AsyncSession = Depends(get_session),
) -> FamilyRepository:
    return FamilyRepository(session)


def get_family_service(
    repo: FamilyRepository = Depends(get_family_repository),
) -> FamilyService:
    return FamilyService(repo)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    family_repo: FamilyRepository = Depends(get_family_repository),
) -> AuthService:
    return AuthService(user_repo, family_repo)


def get_group_repository(
    session: AsyncSession = Depends(get_session),
) -> GroupRepository:
    return GroupRepository(session)


def get_group_service(
    repo: GroupRepository = Depends(get_group_repository),
) -> GroupService:
    return GroupService(repo)


def get_notification_repository(
    session: AsyncSession = Depends(get_session),
) -> NotificationRepository:
    return NotificationRepository(session)


def get_notification_service(
    repo: NotificationRepository = Depends(get_notification_repository),
) -> NotificationService:
    return NotificationService(repo)


def get_setting_repository(
    session: AsyncSession = Depends(get_session),
) -> SettingRepository:
    return SettingRepository(session)


def get_setting_service(
    repo: SettingRepository = Depends(get_setting_repository),
) -> SettingService:
    return SettingService(repo)


def get_report_service(
    session: AsyncSession = Depends(get_session),
) -> ReportService:
    return ReportService(session)
