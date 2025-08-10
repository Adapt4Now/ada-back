import importlib.util
import sys
import types
from pathlib import Path


# Manually create package structure to load schemas without executing package __init__ modules
app_pkg = types.ModuleType("app")
domain_pkg = types.ModuleType("app.domain")
tasks_pkg = types.ModuleType("app.domain.tasks")
app_pkg.domain = domain_pkg  # type: ignore[attr-defined]
domain_pkg.tasks = tasks_pkg  # type: ignore[attr-defined]
sys.modules.setdefault("app", app_pkg)
sys.modules.setdefault("app.domain", domain_pkg)
sys.modules.setdefault("app.domain.tasks", tasks_pkg)
tasks_pkg.__path__ = []  # mark as package for relative imports

# Create minimal models module with TaskStatus enum to satisfy schemas import
models_module = types.ModuleType("app.domain.tasks.models")
sys.modules.setdefault("app.domain.tasks.models", models_module)
exec(
    """
from enum import Enum as PyEnum

class TaskStatus(str, PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
""",
    models_module.__dict__,
)

spec = importlib.util.spec_from_file_location(
    "app.domain.tasks.schemas", Path("app/domain/tasks/schemas.py")
)
schemas = importlib.util.module_from_spec(spec)
assert spec.loader is not None  # for mypy
spec.loader.exec_module(schemas)
TaskCreateSchema = schemas.TaskCreateSchema


def test_task_create_schema_allows_null_assigned_user_id() -> None:
    """TaskCreateSchema should accept None for unassigned tasks."""
    data = TaskCreateSchema(title="Test task", assigned_by_user_id=1)
    assert data.assigned_user_id is None

    explicit_none = TaskCreateSchema(
        title="Another task", assigned_user_id=None, assigned_by_user_id=1
    )
    assert explicit_none.assigned_user_id is None

