"""
Exception Handlers for Console

Defines custom exceptions and helpers for error handling
in batch processes.
"""

from typing import Optional
from datetime import datetime

# Centralized logger
from config.logger import logger


# Custom exceptions

class ProcessError(Exception):
    """Base exception for batch process errors"""
    def __init__(self, process: str, message: str, detail: Optional[str] = None):
        self.process = process
        self.message = message
        self.detail = detail
        self.timestamp = datetime.now()
        super().__init__(self.message)


class DataValidationError(ProcessError):
    """Data validation error"""
    def __init__(self, process: str, field: str, value: any, reason: str):
        self.field = field
        self.value = value
        message = f"Validation failed on field '{field}': {reason}"
        super().__init__(process, message, detail=f"Value: {value}")


class ExternalServiceError(ProcessError):
    """Error communicating with external service"""
    def __init__(self, process: str, service: str, detail: Optional[str] = None):
        self.service = service
        message = f"Error communicating with external service: {service}"
        super().__init__(process, message, detail)


class DatabaseError(ProcessError):
    """Database error"""
    def __init__(self, process: str, operation: str, detail: Optional[str] = None):
        self.operation = operation
        message = f"Error in database operation: {operation}"
        super().__init__(process, message, detail)


class ConfigurationError(Exception):
    """Service configuration error"""
    def __init__(self, parameter: str, reason: str):
        self.parameter = parameter
        self.reason = reason
        message = f"Configuration error in '{parameter}': {reason}"
        super().__init__(message)


class ProcessTimeoutError(ProcessError):
    """Process execution timeout"""
    def __init__(self, process: str, timeout_seconds: int):
        self.timeout_seconds = timeout_seconds
        message = f"Process exceeded timeout of {timeout_seconds} seconds"
        super().__init__(process, message)


# Error handling helpers

def log_error(error: Exception, context: Optional[dict] = None):
    """
    Logs an error with additional context.

    Args:
        error: Exception to log
        context: Additional context information
    """
    error_info = {
        "type": type(error).__name__,
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }

    if context:
        error_info["context"] = context

    if isinstance(error, ProcessError):
        error_info["process"] = error.process
        error_info["detail"] = error.detail

    logger.error(f"Error logged: {error_info}", exc_info=True)

    return error_info


async def handle_process_error(
    error: Exception,
    process: str,
    continue_on_error: bool = False
) -> bool:
    """
    Handles a process error deciding whether to continue or abort.

    Args:
        error: Exception that occurred
        process: Process name
        continue_on_error: Whether to continue executing after error

    Returns:
        True if should continue, False if should abort
    """
    log_error(error, {"process": process})

    # Critical errors that always abort
    critical_errors = (
        ConfigurationError,
        DatabaseError,
        ProcessTimeoutError
    )

    if isinstance(error, critical_errors):
        logger.error(f"❌ Critical error in {process}. Aborting.")
        return False

    # Recoverable errors
    if continue_on_error:
        logger.warning(f"⚠️ Error in {process}. Continuing execution.")
        return True

    return False


def create_error_report(errors: list) -> dict:
    """
    Creates a consolidated error report.

    Args:
        errors: List of errors that occurred

    Returns:
        Dictionary with error report
    """
    if not errors:
        return {
            "total_errors": 0,
            "errors_by_type": {},
            "critical_errors": 0,
            "details": []
        }

    # Count by type
    errors_by_type = {}
    critical_errors = 0

    for error in errors:
        error_type = type(error).__name__
        errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1

        if isinstance(error, (ConfigurationError, DatabaseError, ProcessTimeoutError)):
            critical_errors += 1

    return {
        "total_errors": len(errors),
        "errors_by_type": errors_by_type,
        "critical_errors": critical_errors,
        "details": [
            {
                "type": type(e).__name__,
                "message": str(e),
                "timestamp": getattr(e, 'timestamp', None)
            }
            for e in errors[:10]  # Limit to 10 errors in detail
        ]
    }


class ErrorAccumulator:
    """
    Error accumulator for batch processes.

    Useful for collecting errors during processing and
    generating report at the end.
    """

    def __init__(self):
        self.errors = []
        self.errors_by_type = {}

    def add(self, error: Exception, context: Optional[dict] = None):
        """Adds an error to the accumulator"""
        error_info = log_error(error, context)
        self.errors.append(error_info)

        error_type = type(error).__name__
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1

    def has_errors(self) -> bool:
        """Checks if there are accumulated errors"""
        return len(self.errors) > 0

    def has_critical_errors(self) -> bool:
        """Checks if there are critical errors"""
        return any(
            e.get("type") in ["ConfigurationError", "DatabaseError", "ProcessTimeoutError"]
            for e in self.errors
        )

    def get_report(self) -> dict:
        """Generates error report"""
        return {
            "total": len(self.errors),
            "by_type": self.errors_by_type,
            "critical": self.has_critical_errors(),
            "details": self.errors[:10]  # First 10
        }

    def clear(self):
        """Clears accumulated errors"""
        self.errors = []
        self.errors_by_type = {}


# TODO: Add more exceptions as needed
# Examples:
# - FileProcessingError
# - SFTPError
# - NotificationError
# - RetryExhaustedError
