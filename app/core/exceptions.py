# app/core/exceptions.py
"""Common application level exceptions."""


class AppError(Exception):
    """Base class for all custom application exceptions."""


class NotFoundError(AppError):
    """Raised when a requested entity does not exist."""


class TaskNotFoundError(NotFoundError):
    """Raised when a task is not found in the database."""


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found in the database."""

