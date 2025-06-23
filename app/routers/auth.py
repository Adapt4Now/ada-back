from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.schemas.user import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app.schemas.family import FamilyCreate
from app.schemas.auth import Token, LoginSchema
from app.crud.user import create_user, update_user
from app.crud.family import create_family
from app.models.user import User
from app.core.security import verify_password, create_access_token

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
