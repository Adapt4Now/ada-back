from .auth import router as auth
from .users import router as users
from .groups import router as groups
from .tasks import router as tasks
from .families import router as families
from .reports import router as reports
from .notifications import router as notifications
from .settings import router as settings

__all__ = [
    "auth",
    "users",
    "groups",
    "tasks",
    "families",
    "reports",
    "notifications",
    "settings",
]
