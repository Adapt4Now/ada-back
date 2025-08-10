import logging
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
)

logger = logging.getLogger(__name__)


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


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    logger.error(str(exc), exc_info=exc)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(str(exc), exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
