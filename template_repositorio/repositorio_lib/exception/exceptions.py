"""
Custom exceptions for the repositorio library.

Provides specific exception types for better error handling and debugging.
"""


class RepositoryException(Exception):
    """
    Base exception for all repository-related errors.

    All custom exceptions in this library inherit from this class.
    """
    def __init__(self, message: str = "Repository error occurred"):
        self.message = message
        super().__init__(self.message)


class DatabaseConnectionException(RepositoryException):
    """
    Raised when database connection fails.

    Examples:
        - Cannot connect to PostgreSQL server
        - Connection pool exhausted
        - Authentication failed
    """
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message)


class ModelNotFoundException(RepositoryException):
    """
    Raised when a model is not found in the model_map.

    This typically indicates a typo in the model name or
    that the model hasn't been generated/registered yet.

    Example:
        >>> repo.get_all("invalid_model_name")
        ModelNotFoundException: Model 'invalid_model_name' not found in model_map
    """
    def __init__(self, model_name: str):
        message = f"Model '{model_name}' not found in model_map"
        super().__init__(message)


class ValidationException(RepositoryException):
    """
    Raised when data validation fails.

    Examples:
        - Invalid data types
        - Required fields missing
        - Data constraints violated
    """
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


class CacheException(RepositoryException):
    """
    Raised when cache operations fail.

    Examples:
        - Cache key not found
        - Cache entry expired
        - Cache cleanup failed
    """
    def __init__(self, message: str = "Cache operation failed"):
        super().__init__(message)
