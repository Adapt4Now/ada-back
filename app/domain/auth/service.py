from datetime import datetime, UTC
import logging

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

    def __init__(
        self,
        user_repository_factory,
        family_repository_factory,
        unit_of_work: UnitOfWork,
    ):
        self.user_repository_factory = user_repository_factory
        self.family_repository_factory = family_repository_factory
        self.unit_of_work = unit_of_work

    async def register_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        """Register a new user and create a family for them."""
        logger.info("Registering user")
        async with self.unit_of_work as unit_of_work:
            user_repository = self.user_repository_factory(unit_of_work.session)
            family_repository = self.family_repository_factory(unit_of_work.session)
            new_user = await user_repository.create(user_data)
            family = await family_repository.create(
                FamilyCreate(name=f"{new_user.username}'s family", created_by=new_user.id)
            )
            user = await user_repository.update(
                new_user.id, UserUpdateSchema(family_id=family.id)
            )
        logger.info("Registered user %s", new_user.id)
        return UserResponseSchema.model_validate(user)

    async def login(self, credentials: LoginSchema) -> Token:
        """Authenticate a user and return an access token."""
        if not credentials.username and not credentials.email:
            raise AppError("Username or email required")

        logger.info("User login attempt")
        async with self.unit_of_work as unit_of_work:
            user_repository = self.user_repository_factory(unit_of_work.session)
            user = await user_repository.get_by_username_or_email(
                credentials.username, credentials.email
            )
            if user is None or not verify_password(credentials.password, user.hashed_password):
                raise AppError("Invalid credentials")
            await user_repository.update(
                user.id, UserUpdateSchema(last_login_at=datetime.now(UTC))
            )
        token = create_access_token({"sub": str(user.id)})
        logger.info("User %s logged in", user.id)
        return Token(access_token=token)

    async def request_password_reset(self, data: PasswordResetRequest) -> dict:
        """Generate a password reset token for a user."""
        logger.info("Password reset requested for %s", data.email)
        async with self.unit_of_work as unit_of_work:
            user_repository = self.user_repository_factory(unit_of_work.session)
            token = await user_repository.create_reset_token(data.email)
            if token is None:
                raise UserNotFoundError()
        logger.info("Password reset token created for %s", data.email)
        return {"reset_token": token}

    async def apply_password_reset(self, data: PasswordResetConfirm) -> dict:
        """Apply a password reset using a token."""
        logger.info("Applying password reset")
        async with self.unit_of_work as unit_of_work:
            user_repository = self.user_repository_factory(unit_of_work.session)
            success = await user_repository.reset_password(data.token, data.new_password)
            if not success:
                raise AppError("Invalid or expired token")
        logger.info("Password reset applied")
        return {"message": "Password reset successful"}
