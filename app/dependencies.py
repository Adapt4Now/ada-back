from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.domain.users.repository import UserRepository
from app.domain.users.service import UserService
from app.domain.tasks.repository import TaskRepository
from app.domain.tasks.service import TaskService
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.crud.family import FamilyRepository


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


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    family_repo: FamilyRepository = Depends(get_family_repository),
) -> AuthService:
    return AuthService(user_repo, family_repo)
