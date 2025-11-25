"""
Centralized Logger - Template API

This module configures and exports TWO logger instances for different use cases.
ALL modules must import the appropriate logger from here.

Available Loggers:
    1. logger: Standard logger for simple lifecycle events
    2. structured_logger: Structured logger for business operations with context

Usage Examples:

    # Standard logger - For simple events
    from config.logger import logger
    logger.info("Application started")
    logger.debug("Loading configuration")
    logger.error("Unexpected error", exc_info=True)

    # Structured logger - For business operations with context
    from config.logger import structured_logger
    structured_logger.set_context(request_id="abc123", user_id=456)
    structured_logger.info("Login attempt", username="john", ip="192.168.1.1")
    structured_logger.info("Order created", order_id=789, amount=99.99)
    structured_logger.clear_context()

When to use each:
    - logger: Application lifecycle, configuration, simple debug messages
    - structured_logger: HTTP requests, business transactions, any log you'll query by fields
"""

from repositorio_lib.core import get_logger, get_structured_logger

# Standard logger for simple lifecycle events
logger = get_logger("template_repositorio")

# Structured logger for business operations with context fields
structured_logger = get_structured_logger("template_repositorio")
