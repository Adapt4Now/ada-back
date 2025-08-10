import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jwt import PyJWTError, decode, encode
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import select, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.domain.users.models import User, UserStatus, UserRole
from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError

ALGORITHM = settings.current_config.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.current_config.access_token_expire_minutes
RESET_TOKEN_EXPIRE_MINUTES = settings.current_config.reset_token_expire_minutes
SECRET_KEY = settings.current_config.secret_key

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generate_reset_token() -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=RESET_TOKEN_EXPIRE_MINUTES
    )
    return token, expires_at


def verify_reset_token(user: User, token: str) -> bool:
    return (
        user.reset_token == token
        and user.reset_token_expires_at is not None
        and user.reset_token_expires_at > datetime.now(timezone.utc)
    )


oauth2_scheme = HTTPBearer()


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return the payload."""
    try:
        return decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError as exc:  # noqa: B904 - re-raise with 401
        raise AuthenticationError("Could not validate credentials") from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_database_session),
) -> User:
    """Return the currently authenticated user based on the JWT token."""
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    statement = select(User).where(User.id == bindparam("user_id_param"))
    result = await session.execute(statement, {"user_id_param": int(user_id)})
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthenticationError("User not found")
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """Ensure the user is active."""
    if not user.is_active or user.status != UserStatus.ACTIVE:
        raise AuthenticationError("Inactive user")
    return user


async def get_current_admin(user: User = Depends(get_current_active_user)) -> User:
    """Ensure the user has administrative privileges."""
    if user.role != UserRole.ADMIN:
        raise AuthorizationError("Admin privileges required")
    return user

