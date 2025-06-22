# app/core/exceptions.py

class TaskNotFoundError(Exception):
    """Raised when a task is not found in the database."""
    pass