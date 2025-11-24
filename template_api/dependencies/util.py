"""
Project-specific Utilities for API

Helper functions and utilities specific to this project.
For utilities shared across projects, use repositorio_lib/utils/
"""

from typing import Optional, Dict, Any
from datetime import datetime
import httpx

# Centralized logger
from config.logger import logger


async def validate_request_data(data: dict, required_fields: list) -> tuple[bool, Optional[str]]:
    """
    Validates that a request contains all required fields.

    Args:
        data: Dictionary with request data
        required_fields: List of required fields

    Returns:
        Tuple (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    return True, None


def format_response(data: Any, message: str = "Success", status: int = 200) -> dict:
    """
    Formats a standard API response.

    Args:
        data: Data to return
        message: Descriptive message
        status: HTTP status code

    Returns:
        Dictionary with standard format
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
    Makes a call to an external API with error handling.

    Args:
        url: API URL
        method: HTTP method (GET, POST, etc.)
        headers: Optional HTTP headers
        data: Data for POST/PUT
        timeout: Timeout in seconds

    Returns:
        JSON response from API or None if error
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
                logger.error(f"Unsupported HTTP method: {method}")
                return None

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in external API: {e.response.status_code} - {url}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Connection error with external API: {url} - {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling external API: {e}", exc_info=True)
        return None


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitizes user input to prevent injection.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Truncate if too long
    text = text[:max_length]

    # Remove dangerous characters (adjust as needed)
    dangerous_chars = ['<', '>', '{', '}', '\\', '|']
    for char in dangerous_chars:
        text = text.replace(char, '')

    return text.strip()


def calculate_pagination(total: int, page: int, page_size: int) -> dict:
    """
    Calculates pagination information.

    Args:
        total: Total records
        page: Current page
        page_size: Page size

    Returns:
        Dictionary with pagination info
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
    Logs API call information.

    Args:
        endpoint: Endpoint path
        method: HTTP method
        user: User who made the call
        duration_ms: Duration in milliseconds
        status_code: Response status code
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

    # TODO: If DB persistence is needed
    # await repository.create_log(log_data)


def mask_sensitive_data(data: dict, sensitive_keys: list = None) -> dict:
    """
    Masks sensitive data in a dictionary for logging.

    Args:
        data: Dictionary with data
        sensitive_keys: Keys to mask

    Returns:
        Dictionary with masked data
    """
    if sensitive_keys is None:
        sensitive_keys = ["password", "token", "secret", "api_key", "credit_card"]

    masked_data = data.copy()

    for key in masked_data:
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            masked_data[key] = "***MASKED***"

    return masked_data


# TODO: Add more utilities according to project needs
# Examples:
# - Specific business validations
# - Data formatting
# - Timezone conversions
# - Unique code generation
# - Domain-specific calculations
