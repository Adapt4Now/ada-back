from typing import List, Tuple
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from sqlalchemy import select, bindparam
from starlette.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
import importlib
from types import ModuleType
from app.core.logging import setup_logging
from app.database import DatabaseConfig, DatabaseSessionManager, create_db_manager
from app.dependencies import container
from app.domain.users.models import User, UserRole
from app.domain.users.schemas import UserCreateSchema, UserUpdateSchema
from app.domain.users.repository import UserRepository
from app.core.error_handlers import (
    exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.core.exceptions import AppError
from fastapi import HTTPException
from app.core.config import settings

setup_logging()
logger = logging.getLogger(__name__)


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
    container.db_manager.override(db_manager)
    await ensure_admin_user(db_manager)
    yield
    await db_manager.close()


def discover_router_configs() -> List[Tuple[APIRouter, str, ModuleType]]:
    """Recursively discover routers in app/domain."""
    router_configs: List[Tuple[APIRouter, str, ModuleType]] = []
    app_path = Path(__file__).resolve().parent
    domain_path = app_path / "domain"
    for router_file in domain_path.rglob("api/router.py"):
        relative = router_file.relative_to(app_path)
        module_parts = ("app",) + relative.with_suffix("").parts
        module_name = ".".join(module_parts)
        module = importlib.import_module(module_name)
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            tag = router_file.parent.parent.name.capitalize()
            router_configs.append((router, tag, module))
    return router_configs


class ApplicationSetup:
    """Class for initialization and configuration of FastAPI application"""

    API_PREFIX: str = settings.current_config.api_prefix
    CORS_SETTINGS: dict[str, list[str] | bool] = {
        "allow_origins": settings.current_config.cors_allow_origins,
        "allow_credentials": settings.current_config.cors_allow_credentials,
        "allow_methods": settings.current_config.cors_allow_methods,
        "allow_headers": settings.current_config.cors_allow_headers,
    }

    def __init__(self) -> None:
        self.app = FastAPI(lifespan=lifespan)

    def setup_cors(self) -> None:
        """Configure CORS middleware"""
        self.app.add_middleware(CORSMiddleware, **self.CORS_SETTINGS)

    def register_routers(self) -> List[ModuleType]:
        """Register all application routers"""
        modules: List[ModuleType] = []
        try:
            for router, tag, module in discover_router_configs():
                self.app.include_router(router, prefix=self.API_PREFIX, tags=[tag])
                logger.info(f"Router {tag} registered")
                modules.append(module)
        except Exception as e:
            logger.error(f"Error registering routers: {e}")
            raise
        return modules

    def initialize(self) -> FastAPI:
        """Initialize the application"""
        self.setup_cors()
        modules = self.register_routers()
        self.app.add_exception_handler(AppError, exception_handler)
        self.app.add_exception_handler(HTTPException, http_exception_handler)
        self.app.add_exception_handler(Exception, general_exception_handler)
        container.wire(modules=modules)
        return self.app


app = ApplicationSetup().initialize()
