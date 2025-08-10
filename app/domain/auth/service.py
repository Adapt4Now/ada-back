from datetime import datetime, UTC
import logging

from app.domain.users.repository import UserRepository
from app.domain.families.repository import FamilyRepository
from app.database import UnitOfWork
from app.domain.users.schemas import (
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)
from app.domain.families.schemas import FamilyCreate
from app.domain.auth.schemas import (
    LoginSchema,
    PasswordResetRequest,
    PasswordResetConfirm,
    Token,
)
from app.domain.users.models import User
from app.core.security import create_access_token, verify_password
from app.core.exceptions import AppError, UserNotFoundError

logger = logging.getLogger(__name__)


class AuthService:
    """Service layer for authentication and authorization operations."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def register_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        async with self.uow as uow:
            user_repo = UserRepository(uow.session)
            family_repo = FamilyRepository(uow.session)
            new_user = await user_repo.create(user_data)
            family = await family_repo.create(
                FamilyCreate(name=f"{new_user.username}'s family", created_by=new_user.id)
            )
            user = await user_repo.update(
                new_user.id, UserUpdateSchema(family_id=family.id)
            )
        logger.info("Registered user %s", new_user.id)
        return UserResponseSchema.model_validate(user)

    async def login(self, credentials: LoginSchema) -> Token:
        if not credentials.username and not credentials.email:
            raise AppError("Username or email required")

        async with self.uow as uow:
            user_repo = UserRepository(uow.session)
            user = await user_repo.get_by_username_or_email(
                credentials.username, credentials.email
            )
            if user is None or not verify_password(credentials.password, user.hashed_password):
                raise AppError("Invalid credentials")
            await user_repo.update(
                user.id, UserUpdateSchema(last_login_at=datetime.now(UTC))
            )
        token = create_access_token({"sub": str(user.id)})
        logger.info("User %s logged in", user.id)
        return Token(access_token=token)

    async def request_password_reset(self, data: PasswordResetRequest) -> dict:
        async with self.uow as uow:
            user_repo = UserRepository(uow.session)
            token = await user_repo.create_reset_token(data.email)
            if token is None:
                raise UserNotFoundError()
        logger.info("Password reset requested for %s", data.email)
        return {"reset_token": token}

    async def apply_password_reset(self, data: PasswordResetConfirm) -> dict:
        async with self.uow as uow:
            user_repo = UserRepository(uow.session)
            success = await user_repo.reset_password(data.token, data.new_password)
            if not success:
                raise AppError("Invalid or expired token")
        logger.info("Password reset applied")
        return {"message": "Password reset successful"}
