"""
Configuration module for repositorio_lib.

Contains settings classes and cache configuration.
"""

# settings
from .settings import (
    jwt_settings,
    db_settings,
    app_settings,
    email_settings,
    api_settings,
    web_settings,
    console_settings,
    external_services,
)

# cache
from .cache import cache, SimpleCache, CacheStats, CacheEntry

# env
from .env import APP_ENV

# logger
from .logger import logger, structured_logger

__all__ = [
    # settings
    "jwt_settings",
    "db_settings",
    "app_settings",
    "email_settings",
    "api_settings",
    "web_settings",
    "console_settings",
    "external_services",
    # cache
    "cache",
    "SimpleCache",
    "CacheStats",
    "CacheEntry",
    # env
    "APP_ENV",
    "logger",
    "structured_logger",
]
