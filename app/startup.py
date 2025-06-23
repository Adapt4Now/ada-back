from typing import List, Tuple
from fastapi import FastAPI, APIRouter
from sqlalchemy import select, bindparam
from starlette.middleware.cors import CORSMiddleware
import logging
from app.routers import (
    auth,
    tasks,
    users,
    groups,
    families,
    reports,
    notifications,
    settings,
    admin,
)
from app.database import get_database_session
from app.models.user import User
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from pydantic import EmailStr
from app.crud.user import create_user as crud_create_user, update_user as crud_update_user

# Logger setup
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def ensure_admin_user() -> None:
    """Create the default admin user if it does not exist."""
    async for db in get_database_session():
        stmt = select(User).where(User.username == bindparam("uname"))
        result = await db.execute(stmt, {"uname": "admin"})
        admin_user = result.scalar_one_or_none()
        if admin_user is None:
            await crud_create_user(
                db,
                UserCreateSchema(
                    username="admin",
                    email=EmailStr("admin@example.com"),
                    password="password",
                    is_superuser=True,
                ),
            )
        elif not admin_user.is_superuser:
            await crud_update_user(db, admin_user.id, UserUpdateSchema(is_superuser=True))
        break

class ApplicationSetup:
    """Class for initialization and configuration of FastAPI application"""

    API_PREFIX: str = "/api"
    CORS_SETTINGS: dict[str, list[str] | bool] = {
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }

    def __init__(self) -> None:
        self.app = FastAPI()
        self._router_configs: List[Tuple[APIRouter, str]] = [
            (auth, "Auth"),
            (families, "Families"),
            (groups, "Groups"),
            (tasks, "Tasks"),
            (users, "Users"),
            (reports, "Reports"),
            (notifications, "Notifications"),
            (settings, "Settings"),
            (admin, "Admin"),
        ]

    def setup_cors(self) -> None:
        """Configure CORS middleware"""
        self.app.add_middleware(CORSMiddleware, **self.CORS_SETTINGS)

    def register_routers(self) -> None:
        """Register all application routers"""
        try:
            for router, tag in self._router_configs:
                self.app.include_router(router, prefix=self.API_PREFIX, tags=[tag])
                logger.info(f"Router {tag} registered")
        except Exception as e:
            logger.error(f"Error registering routers: {e}")
            raise

    def initialize(self) -> FastAPI:
        """Initialize the application"""
        self.setup_cors()
        self.register_routers()
        self.app.add_event_handler("startup", ensure_admin_user)
        return self.app


app = ApplicationSetup().initialize()
