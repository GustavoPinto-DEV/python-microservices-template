"""
Centralized Logger - Web Template

This module configures and exports TWO logger instances for different use cases.
ALL modules must import the appropriate logger from here.

Available Loggers:
    1. logger: Standard logger for simple lifecycle events
    2. structured_logger: Structured logger for web requests and user actions

Usage Examples:

    # Standard logger - For simple events
    from config.logger import logger
    logger.info("Web application started")
    logger.debug("Rendering template: dashboard.html")
    logger.error("Template not found", exc_info=True)

    # Structured logger - For user actions and web requests
    from config.logger import structured_logger
    structured_logger.set_context(session_id="xyz789", user_id=456)
    structured_logger.info("Page accessed", page="/dashboard", method="GET")
    structured_logger.info("Form submitted", form="contact", fields=5)
    structured_logger.clear_context()

When to use each:
    - logger: Application startup/shutdown, template rendering, static file serving
    - structured_logger: User sessions, page views, form submissions, any user action
"""

from repositorio_lib.core import get_logger, get_structured_logger

# Standard logger for simple lifecycle events
logger = get_logger("template_web")

# Structured logger for web requests and user actions with context
structured_logger = get_structured_logger("template_web")


__all__ = ["logger", "structured_logger"]
