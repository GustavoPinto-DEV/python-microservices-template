"""
Exception module for repositorio_lib.

Contains custom exceptions for the repository layer.
"""

# exceptions
from .exceptions import (
    RepositoryException,
    DatabaseConnectionException,
    ModelNotFoundException,
    ValidationException,
    CacheException,
)

__all__ = [
    "RepositoryException",
    "DatabaseConnectionException",
    "ModelNotFoundException",
    "ValidationException",
    "CacheException",
]
