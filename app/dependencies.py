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
    user_service = providers.Factory(UserService, repo_factory=user_repository, uow=uow)
    task_service = providers.Factory(TaskService, repo_factory=task_repository, uow=uow)
    admin_service = providers.Factory(AdminService, repo_factory=user_repository, uow=uow)
    auth_service = providers.Factory(
        AuthService,
        user_repo_factory=user_repository,
        family_repo_factory=family_repository,
        uow=uow,
    )
    family_service = providers.Factory(FamilyService, repo_factory=family_repository, uow=uow)
    notification_service = providers.Factory(
        NotificationService, repo_factory=notification_repository, uow=uow
    )
    setting_service = providers.Factory(SettingService, repo_factory=setting_repository, uow=uow)
    group_service = providers.Factory(GroupService, repo_factory=group_repository, uow=uow)
    report_service = providers.Factory(ReportService, uow=uow)


# Global container instance
container = Container()

