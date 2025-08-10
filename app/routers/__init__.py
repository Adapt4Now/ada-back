from .auth import router as auth
from app.domain.users import router as users
from .groups import router as groups
from app.domain.tasks import router as tasks
from .families import router as families
from .reports import router as reports
from .notifications import router as notifications
from .settings import router as settings
from .admin import router as admin

__all__ = [
    "auth",
    "users",
    "groups",
    "tasks",
    "families",
    "reports",
    "notifications",
    "settings",
    "admin",
]
