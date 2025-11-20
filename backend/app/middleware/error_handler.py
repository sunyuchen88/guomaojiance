import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions.

    Args:
        request: The incoming request
        exc: The HTTP exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.

    Args:
        request: The incoming request
        exc: The validation error

    Returns:
        JSON response with validation error details
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Validation error",
            "errors": errors
        },
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors.

    Args:
        request: The incoming request
        exc: The database error

    Returns:
        JSON response with generic error message
    """
    logger.error(f"Database error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "error": str(exc) if logger.level <= logging.DEBUG else "Internal server error"
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions.

    Args:
        request: The incoming request
        exc: The exception

    Returns:
        JSON response with generic error message
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if logger.level <= logging.DEBUG else "An unexpected error occurred"
        },
    )
