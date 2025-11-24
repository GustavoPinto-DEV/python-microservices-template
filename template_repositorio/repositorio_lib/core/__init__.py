"""Core module - Database, logging, and settings"""

# database
from .database import get_db_context, get_async_session

# crud_helpers
from .crud_helpers import (
    get_pk_name,
    get_all_async,
    get_one_by_id_async,
    update_data_async,
    create_data_async,
    delete_data_async,
    bulk_create_async,
    bulk_update_async,
)

# crypto
from .crypto import (
    hash_password,
    verify_password,
    base64_encrypt,
    base64_decrypt,
)

# logger
from .logger import log_performance, get_logger, logger

# security
from .security import create_access_token, verify_token

__all__ = [
    # database
    "get_db_context",
    "get_async_session",
    # crud_helpers
    "get_pk_name",
    "get_all_async",
    "get_one_by_id_async",
    "update_data_async",
    "create_data_async",
    "delete_data_async",
    "bulk_create_async",
    "bulk_update_async",
    # crypto
    "hash_password",
    "verify_password",
    "base64_encrypt",
    "base64_decrypt",
    # logger
    "log_performance",
    "get_logger",
    "logger",
    # security
    "create_access_token",
    "verify_token",
]
