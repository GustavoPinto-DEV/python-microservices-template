"""
Manejadores centralizados de excepciones

Proporciona manejo consistente de errores en toda la API.
Los errores se capturan, logean y formatean apropiadamente.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def registrar_exception_handlers(app: FastAPI) -> None:
    """
    Registra todos los manejadores de excepciones en la aplicación.

    Args:
        app: Instancia de FastAPI
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Maneja excepciones HTTP estándar (404, 403, etc.)
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
        Maneja errores de validación de Pydantic.
        Retorna información detallada de los campos inválidos.
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
                "message": "Error de validación en los datos enviados",
                "details": errors,
                "path": str(request.url.path),
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """
        Maneja errores de valor (ValueError).
        Típicamente usados para validaciones de negocio.
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
        Maneja errores de permisos.
        """
        logger.warning(
            f"Permission Error - Path: {request.url.path} - "
            f"Error: {str(exc)}"
        )

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "PERMISSION_DENIED",
                "message": "No tiene permisos para realizar esta acción",
                "detail": str(exc),
                "path": str(request.url.path),
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Maneja todas las excepciones no capturadas.
        Último recurso para evitar que la API crashee.
        """
        logger.error(
            f"Unhandled Exception - Path: {request.url.path} - "
            f"Type: {type(exc).__name__} - Error: {str(exc)}",
            exc_info=True
        )

        # En producción, no exponer detalles internos
        import os
        is_dev = os.getenv("ENVIRONMENT", "dev") == "dev"

        error_detail = str(exc) if is_dev else "Error interno del servidor"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ha ocurrido un error inesperado",
                "detail": error_detail,
                "path": str(request.url.path),
                "timestamp": datetime.now().isoformat()
            }
        )


# Excepciones personalizadas para el dominio

class BusinessLogicError(Exception):
    """Excepción para errores de lógica de negocio"""
    def __init__(self, message: str, detail: str = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class ResourceNotFoundError(Exception):
    """Excepción cuando un recurso no se encuentra"""
    def __init__(self, resource_type: str, resource_id: any):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.message = f"{resource_type} con ID {resource_id} no encontrado"
        super().__init__(self.message)


class DuplicateResourceError(Exception):
    """Excepción cuando se intenta crear un recurso duplicado"""
    def __init__(self, resource_type: str, field: str, value: any):
        self.resource_type = resource_type
        self.field = field
        self.value = value
        self.message = f"{resource_type} con {field}='{value}' ya existe"
        super().__init__(self.message)


class ExternalServiceError(Exception):
    """Excepción cuando falla una llamada a servicio externo"""
    def __init__(self, service_name: str, detail: str = None):
        self.service_name = service_name
        self.detail = detail
        self.message = f"Error en servicio externo: {service_name}"
        super().__init__(self.message)


# Registrar manejadores para excepciones personalizadas
def register_custom_handlers(app: FastAPI):
    """
    Registra manejadores para excepciones personalizadas.

    Llamar después de registrar_exception_handlers(app).
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


# TODO: Agregar más excepciones personalizadas según necesidad
# Ejemplos:
# - InvalidCredentialsError
# - InsufficientPermissionsError
# - RateLimitExceededError
# - MaintenanceModeError
