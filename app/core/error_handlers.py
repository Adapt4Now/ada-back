from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
)


async def exception_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle application-level exceptions and return JSON responses."""
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    detail = str(exc) or exc.__class__.__name__
    return JSONResponse(status_code=status_code, content={"detail": detail})
