import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.app.models.base import ErrorResponse

logger = logging.getLogger("indusmind-ai")

class APIException(Exception):
    """Base exception for custom API errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, detail: dict = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)

async def global_exception_handler(request: Request, exc: Exception):
    """Catches all unhandled exceptions and returns a 500 error."""
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            message="An unexpected internal server error occurred.",
            detail=str(exc)
        ).model_dump()
    )

async def api_exception_handler(request: Request, exc: APIException):
    """Handles custom APIException gracefully."""
    logger.warning(f"API Exception [{exc.status_code}]: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.message,
            detail=exc.detail
        ).model_dump()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Overrides default validation errors to use the standard ErrorResponse model."""
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            message="Request validation failed.",
            detail=exc.errors()
        ).model_dump()
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Catches FastAPI HTTPExceptions and returns the standard ErrorResponse model."""
    logger.warning(f"HTTP Exception [{exc.status_code}]: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=str(exc.detail),
            success=False
        ).model_dump()
    )
