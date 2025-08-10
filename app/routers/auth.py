from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
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
from app.crud.user import (
    create_reset_token,
    create_user,
    reset_password,
    update_user,
)
from app.crud.family import create_family
from app.models.user import User
from app.core.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateSchema,
    db: AsyncSession = Depends(get_database_session),
) -> UserResponseSchema:
    new_user = await create_user(db, user_data)
    family = await create_family(
        db,
        FamilyCreate(name=f"{new_user.username}'s family", created_by=new_user.id),
    )
    await update_user(db, new_user.id, UserUpdateSchema(family_id=family.id))
    await db.refresh(new_user)
    return UserResponseSchema.model_validate(new_user)


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginSchema,
    db: AsyncSession = Depends(get_database_session),
) -> Token:
    if not credentials.username and not credentials.email:
        raise HTTPException(status_code=400, detail="Username or email required")

    query = select(User)
    params = {}
    if credentials.username:
        query = query.where(User.username == bindparam("u"))
        params["u"] = credentials.username
    else:
        query = query.where(User.email == bindparam("e"))
        params["e"] = credentials.email

    result = await db.execute(query, params)
    user = result.scalar_one_or_none()
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    await update_user(db, user.id, UserUpdateSchema(last_login_at=datetime.now(UTC)))
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.post("/request-password-reset")
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_database_session),
):
    token = await create_reset_token(db, data.email)
    if token is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"reset_token": token}


@router.post("/reset-password")
async def apply_password_reset(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_database_session),
):
    success = await reset_password(db, data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password reset successful"}
