"""
Centralized Exception Handlers

Provides consistent error handling throughout the API.
Errors are caught, logged, and formatted appropriately.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime

# Centralized logger
from config.logger import logger


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers in the application.

    Args:
        app: FastAPI instance
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Handle standard HTTP exceptions (404, 403, etc.)
        """
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail} - "
            f"Path: {request.url.path} - Method: {request.method}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "path": str(request.url.path),
                "method": request.method,
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle Pydantic validation errors.
        Returns detailed information about invalid fields.
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            })

        logger.warning(
            f"Validation Error - Path: {request.url.path} - "
            f"Errors: {len(errors)}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Validation error in submitted data",
                "details": errors,
                "path": str(request.url.path),
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """
        Handle value errors (ValueError).
        Typically used for business validations.
        """
        logger.warning(
            f"Value Error - Path: {request.url.path} - "
            f"Error: {str(exc)}"
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "VALUE_ERROR",
                "message": str(exc),
                "path": str(request.url.path),
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        """
        Handle permission errors.
        """
        logger.warning(
            f"Permission Error - Path: {request.url.path} - "
            f"Error: {str(exc)}"
        )

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "PERMISSION_DENIED",
                "message": "You don't have permissions to perform this action",
                "detail": str(exc),
                "path": str(request.url.path),
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle all uncaught exceptions.
        Last resort to prevent the API from crashing.
        """
        logger.error(
            f"Unhandled Exception - Path: {request.url.path} - "
            f"Type: {type(exc).__name__} - Error: {str(exc)}",
            exc_info=True
        )

        # In production, don't expose internal details
        import os
        is_dev = os.getenv("ENVIRONMENT", "dev") == "dev"

        error_detail = str(exc) if is_dev else "Internal server error"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "detail": error_detail,
                "path": str(request.url.path),
                "timestamp": datetime.now().isoformat()
            }
        )


# Custom exceptions for the domain

class BusinessLogicError(Exception):
    """Exception for business logic errors"""
    def __init__(self, message: str, detail: str = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class ResourceNotFoundError(Exception):
    """Exception when a resource is not found"""
    def __init__(self, resource_type: str, resource_id: any):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(self.message)


class DuplicateResourceError(Exception):
    """Exception when attempting to create a duplicate resource"""
    def __init__(self, resource_type: str, field: str, value: any):
        self.resource_type = resource_type
        self.field = field
        self.value = value
        self.message = f"{resource_type} with {field}='{value}' already exists"
        super().__init__(self.message)


class ExternalServiceError(Exception):
    """Exception when an external service call fails"""
    def __init__(self, service_name: str, detail: str = None):
        self.service_name = service_name
        self.detail = detail
        self.message = f"Error in external service: {service_name}"
        super().__init__(self.message)


# Register handlers for custom exceptions
def register_custom_handlers(app: FastAPI):
    """
    Register handlers for custom exceptions.

    Call after register_exception_handlers(app).
    """

    @app.exception_handler(BusinessLogicError)
    async def business_logic_error_handler(request: Request, exc: BusinessLogicError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "BUSINESS_LOGIC_ERROR",
                "message": exc.message,
                "detail": exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "RESOURCE_NOT_FOUND",
                "message": exc.message,
                "resource_type": exc.resource_type,
                "resource_id": str(exc.resource_id),
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(DuplicateResourceError)
    async def duplicate_resource_handler(request: Request, exc: DuplicateResourceError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "DUPLICATE_RESOURCE",
                "message": exc.message,
                "resource_type": exc.resource_type,
                "field": exc.field,
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(ExternalServiceError)
    async def external_service_error_handler(request: Request, exc: ExternalServiceError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "EXTERNAL_SERVICE_ERROR",
                "message": exc.message,
                "service": exc.service_name,
                "detail": exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        )


# TODO: Add more custom exceptions as needed
# Examples:
# - InvalidCredentialsError
# - InsufficientPermissionsError
# - RateLimitExceededError
# - MaintenanceModeError
