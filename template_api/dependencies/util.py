"""
Utilidades específicas del proyecto API

Funciones helper y utilities que son específicas de este proyecto.
Para utilidades compartidas entre proyectos, usar repositorio_lib/utils/
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


async def validate_request_data(data: dict, required_fields: list) -> tuple[bool, Optional[str]]:
    """
    Valida que un request contenga todos los campos requeridos.

    Args:
        data: Diccionario con datos del request
        required_fields: Lista de campos requeridos

    Returns:
        Tupla (es_valido, mensaje_error)
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]

    if missing_fields:
        return False, f"Campos requeridos faltantes: {', '.join(missing_fields)}"

    return True, None


def format_response(data: Any, message: str = "Éxito", status: int = 200) -> dict:
    """
    Formatea una respuesta estándar de la API.

    Args:
        data: Datos a retornar
        message: Mensaje descriptivo
        status: Código de estado HTTP

    Returns:
        Diccionario con formato estándar
    """
    return {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


async def call_external_api(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[dict] = None,
    timeout: int = 30
) -> Optional[dict]:
    """
    Realiza una llamada a una API externa con manejo de errores.

    Args:
        url: URL de la API
        method: Método HTTP (GET, POST, etc.)
        headers: Headers HTTP opcionales
        data: Datos para POST/PUT
        timeout: Timeout en segundos

    Returns:
        Response JSON de la API o None si hay error
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                logger.error(f"Método HTTP no soportado: {method}")
                return None

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP en API externa: {e.response.status_code} - {url}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Error de conexión con API externa: {url} - {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado llamando API externa: {e}", exc_info=True)
        return None


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitiza input de usuario para prevenir inyección.

    Args:
        text: Texto a sanitizar
        max_length: Longitud máxima permitida

    Returns:
        Texto sanitizado
    """
    if not text:
        return ""

    # Truncar si es muy largo
    text = text[:max_length]

    # Remover caracteres peligrosos (ajustar según necesidad)
    dangerous_chars = ['<', '>', '{', '}', '\\', '|']
    for char in dangerous_chars:
        text = text.replace(char, '')

    return text.strip()


def calculate_pagination(total: int, page: int, page_size: int) -> dict:
    """
    Calcula información de paginación.

    Args:
        total: Total de registros
        page: Página actual
        page_size: Tamaño de página

    Returns:
        Diccionario con info de paginación
    """
    import math

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    offset = (page - 1) * page_size

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "offset": offset,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


async def log_api_call(
    endpoint: str,
    method: str,
    user: Optional[str] = None,
    duration_ms: Optional[float] = None,
    status_code: Optional[int] = None
) -> None:
    """
    Registra información de llamadas a la API.

    Args:
        endpoint: Ruta del endpoint
        method: Método HTTP
        user: Usuario que hizo la llamada
        duration_ms: Duración en milisegundos
        status_code: Código de estado de respuesta
    """
    log_data = {
        "endpoint": endpoint,
        "method": method,
        "user": user or "anonymous",
        "duration_ms": duration_ms,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"API Call: {log_data}")

    # TODO: Si se necesita persistir en BD
    # await repository.create_log(log_data)


def mask_sensitive_data(data: dict, sensitive_keys: list = None) -> dict:
    """
    Enmascara datos sensibles en un diccionario para logging.

    Args:
        data: Diccionario con datos
        sensitive_keys: Claves a enmascarar

    Returns:
        Diccionario con datos enmascarados
    """
    if sensitive_keys is None:
        sensitive_keys = ["password", "token", "secret", "api_key", "credit_card"]

    masked_data = data.copy()

    for key in masked_data:
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            masked_data[key] = "***MASKED***"

    return masked_data


# TODO: Agregar más utilidades según necesidad del proyecto
# Ejemplos:
# - Validaciones de negocio específicas
# - Formateo de datos
# - Conversiones de timezone
# - Generación de códigos únicos
# - Cálculos específicos del dominio
