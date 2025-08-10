from typing import List, Tuple
from contextlib import asynccontextmanager
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
from app.database import DatabaseConfig, DatabaseSessionManager, create_db_manager
from app.models.user import User, UserRole
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from pydantic import EmailStr
from app.crud.user import UserRepository
from app.core.error_handlers import exception_handler
from app.core.exceptions import AppError

# Logger setup
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def ensure_admin_user(db_manager: DatabaseSessionManager) -> None:
    """Create the default admin user if it does not exist."""
    async for db in db_manager.get_session():
        stmt = select(User).where(User.username == bindparam("uname"))
        result = await db.execute(stmt, {"uname": "admin"})
        admin_user = result.scalar_one_or_none()
        repo = UserRepository(db)
        if admin_user is None:
            await repo.create(
                UserCreateSchema(
                    username="admin",
                    email="admin@example.com",
                    password="password",
                    role=UserRole.ADMIN,
                )
            )
        elif admin_user.role != UserRole.ADMIN:
            await repo.update(admin_user.id, UserUpdateSchema(role=UserRole.ADMIN))
        break


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    db_manager = create_db_manager(DatabaseConfig())
    app.state.db_manager = db_manager
    await ensure_admin_user(db_manager)
    yield
    await db_manager.close()

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
        self.app = FastAPI(lifespan=lifespan)
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
        self.app.add_exception_handler(AppError, exception_handler)
        return self.app


app = ApplicationSetup().initialize()
