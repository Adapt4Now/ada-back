from datetime import datetime, UTC
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.schemas.user import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app.schemas.family import FamilyCreate
from app.schemas.auth import (
    LoginSchema,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
)
from app.crud.user import UserRepository
from app.crud.family import FamilyRepository
from app.models.user import User
from app.core.security import create_access_token, verify_password
from app.core.exceptions import AppError, UserNotFoundError
router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_repository(
    db: AsyncSession = Depends(get_database_session),
) -> UserRepository:
    return UserRepository(db)


def get_family_repository(
    db: AsyncSession = Depends(get_database_session),
) -> FamilyRepository:
    return FamilyRepository(db)


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateSchema,
    user_repo: UserRepository = Depends(get_user_repository),
    family_repo: FamilyRepository = Depends(get_family_repository),
) -> UserResponseSchema:
    new_user = await user_repo.create(user_data)
    family = await family_repo.create(
        FamilyCreate(name=f"{new_user.username}'s family", created_by=new_user.id)
    )
    user = await user_repo.update(new_user.id, UserUpdateSchema(family_id=family.id))
    return UserResponseSchema.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginSchema,
    repo: UserRepository = Depends(get_user_repository),
) -> Token:
    if not credentials.username and not credentials.email:
        raise AppError("Username or email required")

    query = select(User)
    params = {}
    if credentials.username:
        query = query.where(User.username == bindparam("u"))
        params["u"] = credentials.username
    else:
        query = query.where(User.email == bindparam("e"))
        params["e"] = credentials.email

    result = await repo.db.execute(query, params)
    user = result.scalar_one_or_none()
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise AppError("Invalid credentials")

    await repo.update(user.id, UserUpdateSchema(last_login_at=datetime.now(UTC)))
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.post("/request-password-reset")
async def request_password_reset(
    data: PasswordResetRequest,
    repo: UserRepository = Depends(get_user_repository),
):
    token = await repo.create_reset_token(data.email)
    if token is None:
        raise UserNotFoundError()
    return {"reset_token": token}


@router.post("/reset-password")
async def apply_password_reset(
    data: PasswordResetConfirm,
    repo: UserRepository = Depends(get_user_repository),
):
    success = await repo.reset_password(data.token, data.new_password)
    if not success:
        raise AppError("Invalid or expired token")
    return {"message": "Password reset successful"}
