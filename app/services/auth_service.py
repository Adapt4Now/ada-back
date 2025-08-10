from datetime import datetime, UTC
from sqlalchemy import select, bindparam

from app.crud.user import UserRepository
from app.crud.family import FamilyRepository
from app.schemas.user import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app.schemas.family import FamilyCreate
from app.schemas.auth import (
    LoginSchema,
    PasswordResetRequest,
    PasswordResetConfirm,
    Token,
)
from app.models.user import User
from app.core.security import create_access_token, verify_password
from app.core.exceptions import AppError, UserNotFoundError


class AuthService:
    """Service layer for authentication and authorization operations."""

    def __init__(self, user_repo: UserRepository, family_repo: FamilyRepository):
        self.user_repo = user_repo
        self.family_repo = family_repo

    async def register_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        new_user = await self.user_repo.create(user_data)
        family = await self.family_repo.create(
            FamilyCreate(name=f"{new_user.username}'s family", created_by=new_user.id)
        )
        user = await self.user_repo.update(
            new_user.id, UserUpdateSchema(family_id=family.id)
        )
        return UserResponseSchema.model_validate(user)

    async def login(self, credentials: LoginSchema) -> Token:
        if not credentials.username and not credentials.email:
            raise AppError("Username or email required")

        query = select(User)
        params: dict[str, str] = {}
        if credentials.username:
            query = query.where(User.username == bindparam("u"))
            params["u"] = credentials.username
        else:
            query = query.where(User.email == bindparam("e"))
            params["e"] = credentials.email

        result = await self.user_repo.db.execute(query, params)
        user = result.scalar_one_or_none()
        if user is None or not verify_password(credentials.password, user.hashed_password):
            raise AppError("Invalid credentials")

        await self.user_repo.update(
            user.id, UserUpdateSchema(last_login_at=datetime.now(UTC))
        )
        token = create_access_token({"sub": str(user.id)})
        return Token(access_token=token)

    async def request_password_reset(self, data: PasswordResetRequest) -> dict:
        token = await self.user_repo.create_reset_token(data.email)
        if token is None:
            raise UserNotFoundError()
        return {"reset_token": token}

    async def apply_password_reset(self, data: PasswordResetConfirm) -> dict:
        success = await self.user_repo.reset_password(data.token, data.new_password)
        if not success:
            raise AppError("Invalid or expired token")
        return {"message": "Password reset successful"}
