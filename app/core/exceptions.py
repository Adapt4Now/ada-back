# app/core/exceptions.py
"""Common application level exceptions."""


class AppError(Exception):
    """Base class for all custom application exceptions."""

    status_code: int = 500
    detail: str = "Application error"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.detail)


class NotFoundError(AppError):
    """Raised when a requested entity does not exist."""

    status_code = 404
    detail = "Resource not found"


class TaskNotFoundError(NotFoundError):
    """Raised when a task is not found in the database."""

    detail = "Task not found"


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found in the database."""

    detail = "User not found"


class GroupNotFoundError(NotFoundError):
    """Raised when a group is not found in the database."""

    detail = "Group not found"


class NotificationNotFoundError(NotFoundError):
    """Raised when a notification is not found."""

    detail = "Notification not found"


class FamilyNotFoundError(NotFoundError):
    """Raised when a family is not found in the database."""

    detail = "Family not found"

