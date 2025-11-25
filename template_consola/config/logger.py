"""
Centralized Logger - Console Template

This module configures and exports TWO logger instances for different use cases.
ALL modules must import the appropriate logger from here.

Available Loggers:
    1. logger: Standard logger for simple lifecycle events
    2. structured_logger: Structured logger for batch processing with metrics

Usage Examples:

    # Standard logger - For simple events
    from config.logger import logger
    logger.info("Console service starting")
    logger.debug("Loading process configuration")
    logger.error("Process initialization failed", exc_info=True)

    # Structured logger - For batch processing with metrics
    from config.logger import structured_logger
    structured_logger.set_context(job_id="batch_001", execution_date="2025-11-25")
    structured_logger.info("Batch processing started", records_total=1000)
    structured_logger.info("Processing progress", processed=500, failed=5)
    structured_logger.info("Batch completed", successful=995, failed=5, duration_sec=45.2)
    structured_logger.clear_context()

When to use each:
    - logger: Service startup/shutdown, configuration loading, simple debug
    - structured_logger: Batch jobs, data processing, any operation you'll track metrics for
"""

from repositorio_lib.core import get_logger, get_structured_logger

# Standard logger for simple lifecycle events
logger = get_logger("template_consola")

# Structured logger for batch processing with metrics and context
structured_logger = get_structured_logger("template_consola")


__all__ = ["logger", "structured_logger"]
