from fastapi import Depends, Request

from app.database import UnitOfWork, DatabaseSessionManager
from app.domain.users.service import UserService
from app.domain.tasks.service import TaskService
from app.domain.admin.service import AdminService
from app.domain.auth.service import AuthService
from app.domain.families.service import FamilyService
from app.domain.notifications.service import NotificationService
from app.domain.settings.service import SettingService
from app.domain.groups.service import GroupService
from app.domain.reports.service import ReportService


def get_uow(request: Request) -> UnitOfWork:
    db_manager: DatabaseSessionManager = request.app.state.db_manager
    return UnitOfWork(db_manager.session_factory)


def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    return UserService(uow)


def get_task_service(uow: UnitOfWork = Depends(get_uow)) -> TaskService:
    return TaskService(uow)


def get_admin_service(uow: UnitOfWork = Depends(get_uow)) -> AdminService:
    return AdminService(uow)


def get_family_service(uow: UnitOfWork = Depends(get_uow)) -> FamilyService:
    return FamilyService(uow)


def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow)


def get_group_service(uow: UnitOfWork = Depends(get_uow)) -> GroupService:
    return GroupService(uow)


def get_notification_service(uow: UnitOfWork = Depends(get_uow)) -> NotificationService:
    return NotificationService(uow)


def get_setting_service(uow: UnitOfWork = Depends(get_uow)) -> SettingService:
    return SettingService(uow)


def get_report_service(uow: UnitOfWork = Depends(get_uow)) -> ReportService:
    return ReportService(uow)

