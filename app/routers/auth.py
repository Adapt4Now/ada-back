from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.schemas.user import UserCreateSchema, UserResponseSchema
from app.schemas.auth import (
    LoginSchema,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
)
from app.crud.user import UserRepository
from app.crud.family import FamilyRepository
from app.services.auth_service import AuthService
router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_repository(
    db: AsyncSession = Depends(get_database_session),
) -> UserRepository:
    return UserRepository(db)


def get_family_repository(
    db: AsyncSession = Depends(get_database_session),
) -> FamilyRepository:
    return FamilyRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    family_repo: FamilyRepository = Depends(get_family_repository),
) -> AuthService:
    return AuthService(user_repo, family_repo)


@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserCreateSchema,
    service: AuthService = Depends(get_auth_service),
) -> UserResponseSchema:
    return await service.register_user(user_data)


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginSchema,
    service: AuthService = Depends(get_auth_service),
) -> Token:
    return await service.login(credentials)


@router.post("/request-password-reset")
async def request_password_reset(
    data: PasswordResetRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.request_password_reset(data)


@router.post("/reset-password")
async def apply_password_reset(
    data: PasswordResetConfirm,
    service: AuthService = Depends(get_auth_service),
):
    return await service.apply_password_reset(data)
