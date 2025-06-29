import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jwt import PyJWTError, decode, encode
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import select, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.models.user import User

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = HTTPBearer()


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return the payload."""
    try:
        return decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError as exc:  # noqa: B904 - re-raise with HTTP 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_database_session),
) -> User:
    """Return the currently authenticated user based on the JWT token."""
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    stmt = select(User).where(User.id == bindparam("uid"))
    result = await db.execute(stmt, {"uid": int(user_id)})
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """Ensure the user is active."""
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user


async def get_current_superuser(user: User = Depends(get_current_active_user)) -> User:
    """Ensure the user has administrative privileges."""
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user

