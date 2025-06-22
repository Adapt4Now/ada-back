from typing import List, Tuple, Type
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
import logging
from app.routers import (
    tasks,
    users,
    groups,
    reports,
    notifications,
    settings,
)

# Logger setup
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
            (groups.router, "Groups"),
            (tasks.router, "Tasks"),
            (users.router, "Users"),
            (reports.router, "Reports"),
            (notifications.router, "Notifications"),
            (settings.router, "Settings"),
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
        return self.app


app = ApplicationSetup().initialize()