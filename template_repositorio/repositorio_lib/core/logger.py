"""
Logging Configuration - Centralized logging setup

Centralized logging system with file rotation, consistent formatting
and support for multiple environments (dev, QA, PRD).
"""

import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from datetime import datetime
from contextlib import contextmanager

from repositorio_lib.config import app_settings


def setup_logger(
    name: str = "repositorio",
    level: int = logging.INFO,
    log_to_file: bool = True,
    propagate: bool = False,
) -> logging.Logger:
    """
    Configure and return a logger with consistent format and handlers.

    IMPORTANT: Use ONE SINGLE logger per complete application.
    - Correct: "template_api", "template_consola", "template_web"
    - Incorrect: "template_api.controller.user", "template_api.controller.v1Controller"

    Args:
        name: Logger name (application name, NOT module name)
        level: Logging level (logging.INFO, logging.DEBUG, etc.)
        log_to_file: If True, saves logs to file with rotation
        propagate: If True, propagates logs to parent logger (default False)

    Returns:
        logging.Logger: Configured logger with console and file handlers

    Features:
        - Detailed format with timestamp, level, name, function and line
        - Automatic file rotation (10 MB max, 5 backups)
        - Date-based organization (YYYY-MM-DD folder)
        - Thread-safe for concurrent applications
        - Auto-detection of environment (dev/QA/PRD)

    Usage:
        >>> from repositorio_lib.core.logger import setup_logger
        >>> # In your application's main.py:
        >>> logger = setup_logger("template_api", level=logging.INFO, log_to_file=True)
        >>> logger.info("Log message")
        >>> logger.debug("Debug details")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = propagate
    if logger.handlers:
        return logger
    log_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    if log_to_file:
        try:
            log_path = app_settings.get_log_dir()
            log_path.mkdir(parents=True, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            today_path = log_path / today
            today_path.mkdir(exist_ok=True)
            log_file = today_path / f"{name}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(log_format)
            logger.addHandler(file_handler)
            logger.debug(f"Log file configured: {log_file}")
        except Exception as e:
            logger.warning(f"Could not configure file logging: {e}")
    return logger


@contextmanager
def log_performance(
    logger: logging.Logger, operation: str, threshold_ms: float = 1000.0
):
    """
    Context manager to measure and log operation execution time.

    Args:
        logger: Logger where to record the measurement
        operation: Descriptive name of the operation
        threshold_ms: Threshold in ms to consider the operation slow (default 1000ms)

    Usage:
        >>> with log_performance(logger, "Database query"):
        ...     result = await db.execute(query)

        >>> with log_performance(logger, "OCR processing", threshold_ms=500):
        ...     text = extract_text(image)

    Logs:
        - DEBUG: If the operation is fast (< threshold)
        - WARNING: If the operation is slow (>= threshold)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms >= threshold_ms:
            logger.warning(
                f"{operation} took {elapsed_ms:.2f}ms (slow - threshold: {threshold_ms}ms)"
            )
        else:
            logger.debug(f"{operation} completed in {elapsed_ms:.2f}ms")


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default configuration.

    IMPORTANT: This method is mainly for internal use by repositorio_lib.
    In your applications (API, Web, Console), you should:
    1. Configure the logger ONCE in main.py or config/logger.py
    2. Import that logger in all modules

    Args:
        name: Logger name (application name)

    Returns:
        logging.Logger: Configured logger

    Note:
        If the logger already exists with handlers, returns it without modification.
        If it has no handlers, configures it with setup_logger().
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


logger = get_logger("repositorio")
