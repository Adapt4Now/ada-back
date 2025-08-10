from fastapi import APIRouter, Depends, status

from app.domain.users.schemas import UserCreateSchema, UserResponseSchema
from app.schemas.auth import (
    LoginSchema,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
)
from app.dependencies import get_auth_service
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


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
