from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from app.domain.users.schemas import UserCreateSchema, UserResponseSchema
from app.domain.auth.schemas import (
    LoginSchema,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
)
from app.dependencies import Container
from app.domain.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def register_user(
    user_data: UserCreateSchema,
    service: AuthService = Depends(Provide[Container.auth_service]),
) -> UserResponseSchema:
    return await service.register_user(user_data)


@router.post("/login", response_model=Token)
@inject
async def login(
    credentials: LoginSchema,
    service: AuthService = Depends(Provide[Container.auth_service]),
) -> Token:
    return await service.login(credentials)


@router.post("/request-password-reset")
@inject
async def request_password_reset(
    data: PasswordResetRequest,
    service: AuthService = Depends(Provide[Container.auth_service]),
):
    return await service.request_password_reset(data)


@router.post("/reset-password")
@inject
async def apply_password_reset(
    data: PasswordResetConfirm,
    service: AuthService = Depends(Provide[Container.auth_service]),
):
    return await service.apply_password_reset(data)
