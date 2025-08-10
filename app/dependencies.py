"""Application dependency injection container."""

from dependency_injector import containers, providers

from app.database import UnitOfWork, DatabaseSessionManager
from app.domain.users.repository import UserRepository
from app.domain.tasks.repository import TaskRepository
from app.domain.families.repository import FamilyRepository
from app.domain.notifications.repository import NotificationRepository
from app.domain.settings.repository import SettingRepository
from app.domain.groups.repository import GroupRepository

from app.domain.users.service import UserService
from app.domain.tasks.service import TaskService
from app.domain.admin.service import AdminService
from app.domain.auth.service import AuthService
from app.domain.families.service import FamilyService
from app.domain.notifications.service import NotificationService
from app.domain.settings.service import SettingService
from app.domain.groups.service import GroupService
from app.domain.reports.service import ReportService


class Container(containers.DeclarativeContainer):
    """Dependency injection container for application components."""

    db_manager = providers.Dependency(instance_of=DatabaseSessionManager)

    # Unit of work provider
    uow = providers.Factory(UnitOfWork, session_factory=db_manager.provided.session_factory)

    # Repository providers
    user_repository = providers.Factory(UserRepository)
    task_repository = providers.Factory(TaskRepository)
    family_repository = providers.Factory(FamilyRepository)
    notification_repository = providers.Factory(NotificationRepository)
    setting_repository = providers.Factory(SettingRepository)
    group_repository = providers.Factory(GroupRepository)

    # Service providers
    user_service = providers.Factory(UserService, uow=uow)
    task_service = providers.Factory(TaskService, uow=uow)
    admin_service = providers.Factory(AdminService, uow=uow)
    auth_service = providers.Factory(AuthService, uow=uow)
    family_service = providers.Factory(FamilyService, uow=uow)
    notification_service = providers.Factory(NotificationService, uow=uow)
    setting_service = providers.Factory(SettingService, uow=uow)
    group_service = providers.Factory(GroupService, uow=uow)
    report_service = providers.Factory(ReportService, uow=uow)


# Global container instance
container = Container()

