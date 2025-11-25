"""
Centralized Logging System

Production-ready logging implementation with:
- Automatic daily folder creation and rotation
- Thread-safe operations for concurrent applications
- Proper handler management to prevent duplicates
- Structured logging with context support
- Performance monitoring utilities
- Graceful error handling and fallback mechanisms

Key Features:
1. Daily rotation WITHOUT service restart (checks date on every log)
2. Prevents handler duplication with proper cleanup
3. Thread-safe for Uvicorn workers and async operations
4. Structured logging with context fields
5. Better error handling and fallback to console
6. Memory-efficient with proper handler lifecycle management
"""

import logging
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler

from repositorio_lib.config import app_settings


class DailyRotatingFileHandler(logging.Handler):
    """
    Custom handler that rotates log files daily by creating dated folders.

    This handler solves the critical issue where logs stop being written after
    24-48 hours because the date is only calculated once at startup.

    Features:
    - Checks current date on EVERY log entry (not just at startup)
    - Automatically creates new daily folders (logs/YYYY-MM-DD/)
    - Closes old handlers properly to prevent resource leaks
    - Thread-safe with lock mechanisms for concurrent writes
    - Size-based rotation within each day (configurable)
    - Graceful fallback to console if file writing fails

    Thread Safety:
        Uses threading.Lock to prevent race conditions when:
        - Multiple workers write simultaneously
        - Day changes during concurrent operations
        - Handler rotation occurs during active logging

    Performance:
        - Date check is fast (string comparison)
        - Lock is held only during rotation (rare operation)
        - No impact on normal logging operations
    """

    def __init__(
        self,
        log_dir: Path,
        service_name: str,
        level: int = logging.INFO,
        encoding: str = "utf-8",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
    ):
        """
        Initialize the daily rotating file handler.

        Args:
            log_dir: Base directory for logs (e.g., /var/log/app/logs)
            service_name: Name of the service (used in filename)
            level: Minimum logging level to handle
            encoding: File encoding (default: utf-8)
            max_bytes: Max file size before size-based rotation (default: 10 MB)
            backup_count: Number of backup files to keep per day (default: 5)
        """
        super().__init__(level)
        self.log_dir = Path(log_dir)
        self.service_name = service_name
        self.encoding = encoding
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # State tracking
        self.current_date: Optional[str] = None
        self.current_handler: Optional[RotatingFileHandler] = None

        # Thread safety
        self.lock = threading.Lock()

        # Initial setup
        self._rotate_if_needed()

    def _get_current_date_str(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        return datetime.now().strftime("%Y-%m-%d")

    def _rotate_if_needed(self) -> bool:
        """
        Check if rotation is needed and perform it.

        This method is called before EVERY log write to ensure logs are
        always written to the correct daily folder.

        Returns:
            bool: True if rotation succeeded or wasn't needed, False if failed
        """
        today = self._get_current_date_str()

        # No rotation needed if same day and handler exists
        if today == self.current_date and self.current_handler is not None:
            return True

        # Day changed or first run - rotate!
        try:
            # Close old handler properly to release file descriptor
            if self.current_handler:
                try:
                    self.current_handler.close()
                except Exception as close_error:
                    print(
                        f"Warning closing old handler: {close_error}",
                        file=sys.stderr,
                    )

            # Create today's folder
            today_path = self.log_dir / today
            today_path.mkdir(parents=True, exist_ok=True)

            # Create log file path
            log_file = today_path / f"{self.service_name}.log"

            # Create new rotating file handler
            self.current_handler = RotatingFileHandler(
                filename=log_file,
                mode="a",  # Append mode
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding=self.encoding,
            )

            # Apply formatter if set
            if self.formatter:
                self.current_handler.setFormatter(self.formatter)

            # Update current date
            self.current_date = today

            # Log success to stdout (visible in Docker logs)
            print(
                f"Log rotated successfully: {log_file} "
                f"(max_size={self.max_bytes / 1024 / 1024:.1f}MB, "
                f"backups={self.backup_count})",
                file=sys.stdout,
            )
            return True

        except Exception as e:
            print(
                f"Error rotating log file: {e.__class__.__name__}: {e}",
                file=sys.stderr,
            )
            return False

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record.

        This is called for EVERY log entry. It checks if rotation is needed
        before writing to ensure logs go to the correct daily file.

        Args:
            record: The log record to emit
        """
        with self.lock:
            # Check if we need to rotate (day change check)
            if not self._rotate_if_needed():
                # Rotation failed - fall back to stderr
                try:
                    formatted = self.format(record)
                    print(
                        f"[FALLBACK] {formatted}",
                        file=sys.stderr,
                    )
                except Exception:
                    pass  # Avoid cascading errors
                return

            # Write log to current handler
            if self.current_handler:
                try:
                    self.current_handler.emit(record)
                except Exception as e:
                    # Writing failed - fall back to stderr
                    try:
                        formatted = self.format(record)
                        print(
                            f"[WRITE ERROR] {e}: {formatted}",
                            file=sys.stderr,
                        )
                    except Exception:
                        pass  # Avoid cascading errors

    def close(self) -> None:
        """Close the handler and release resources."""
        with self.lock:
            if self.current_handler:
                try:
                    self.current_handler.close()
                except Exception:
                    pass  # Ignore errors during shutdown
                self.current_handler = None
        super().close()


class StructuredLogger:
    """
    Wrapper around logging.Logger that adds structured logging capabilities.

    This class allows adding context fields to log messages, making it easier
    to filter and analyze logs in production environments.

    Usage:
        >>> structured_logger = StructuredLogger(logger)
        >>> structured_logger.set_context(request_id="abc123", user_id=456)
        >>> structured_logger.info("User logged in", ip="1.2.3.4")
        >>> # Output: 2025-11-25 10:00:00 | INFO | ... | User logged in | request_id=abc123 user_id=456 ip=1.2.3.4
    """

    def __init__(self, logger: logging.Logger):
        """
        Initialize structured logger wrapper.

        Args:
            logger: The underlying logger instance
        """
        self._logger = logger
        self._context: Dict[str, Any] = {}

    def set_context(self, **kwargs) -> None:
        """
        Set context fields that will be included in all subsequent logs.

        Args:
            **kwargs: Context key-value pairs
        """
        self._context.update(kwargs)

    def clear_context(self) -> None:
        """Clear all context fields."""
        self._context.clear()

    def _format_fields(self, fields: Dict[str, Any]) -> str:
        """Format fields as key=value pairs."""
        if not fields:
            return ""
        return " | " + " ".join(f"{k}={v}" for k, v in fields.items())

    def _log(self, level: int, msg: str, **fields) -> None:
        """Internal log method with field support."""
        all_fields = {**self._context, **fields}
        formatted_fields = self._format_fields(all_fields)
        self._logger.log(level, f"{msg}{formatted_fields}")

    def debug(self, msg: str, **fields) -> None:
        """Log debug message with optional fields."""
        self._log(logging.DEBUG, msg, **fields)

    def info(self, msg: str, **fields) -> None:
        """Log info message with optional fields."""
        self._log(logging.INFO, msg, **fields)

    def warning(self, msg: str, **fields) -> None:
        """Log warning message with optional fields."""
        self._log(logging.WARNING, msg, **fields)

    def error(self, msg: str, exc_info: bool = False, **fields) -> None:
        """Log error message with optional fields and exception info."""
        all_fields = {**self._context, **fields}
        formatted_fields = self._format_fields(all_fields)
        self._logger.error(f"{msg}{formatted_fields}", exc_info=exc_info)

    def critical(self, msg: str, exc_info: bool = False, **fields) -> None:
        """Log critical message with optional fields and exception info."""
        all_fields = {**self._context, **fields}
        formatted_fields = self._format_fields(all_fields)
        self._logger.critical(f"{msg}{formatted_fields}", exc_info=exc_info)

    @property
    def logger(self) -> logging.Logger:
        """Get the underlying logger instance."""
        return self._logger


def setup_logger(
    name: str = "repositorio",
    level: int = logging.INFO,
    propagate: bool = False,
) -> logging.Logger:
    """
    Configure and return a centralized logger with daily rotation.

    CORRECTED VERSION - Key improvements:
    1. Automatic daily folder creation and rotation
    2. Thread-safe operations
    3. Proper handler management (no duplicates)
    4. File logging ALWAYS enabled (production-first design)

    IMPORTANT: Use ONE logger per application (not per module):
        Correct: "template_api", "template_web", "template_console"
        Wrong: "template_api.controller.user", "template_api.router.v1"

    Args:
        name: Logger name (application name, NOT module name)
        level: Logging level (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
        propagate: If True, propagates logs to parent logger (default False)

    Returns:
        logging.Logger: Configured logger instance

    Features:
        - Daily folder creation (logs/YYYY-MM-DD/)
        - Automatic rotation at midnight (no restart needed)
        - Size-based rotation within each day (10 MB max, 5 backups)
        - Thread-safe for concurrent operations
        - Console output to stdout
        - Graceful fallback if file writing fails
        - File logging ALWAYS enabled

    Usage:
        >>> # In your application's main.py or config/logger.py:
        >>> from repositorio_lib.core.logger import setup_logger
        >>> logger = setup_logger("template_api", level=logging.INFO)
        >>>
        >>> # In all other modules:
        >>> from config.logger import logger
        >>> logger.info("Application started")

    Folder Structure:
        logs/
        ├── 2025-11-25/
        │   ├── template_api.log      # Current log
        │   ├── template_api.log.1    # Size rotation backup
        │   └── template_api.log.2
        ├── 2025-11-26/               # Created automatically at midnight
        │   └── template_api.log
        └── 2025-11-27/
            └── template_api.log
    """
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = propagate

    # If logger already has handlers, return it to prevent duplicates
    if logger.handlers:
        return logger

    # Create consistent formatter
    log_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (stdout) - always enabled
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # File handler with daily rotation - ALWAYS enabled
    try:
        log_path = app_settings.get_log_dir()
        log_path.mkdir(parents=True, exist_ok=True)

        # Use DailyRotatingFileHandler (not RotatingFileHandler)
        daily_handler = DailyRotatingFileHandler(
            log_dir=log_path,
            service_name=name,
            level=level,
            encoding="utf-8",
            max_bytes=10 * 1024 * 1024,  # 10 MB per file
            backup_count=5,  # Keep 5 backup files per day
        )
        daily_handler.setFormatter(log_format)
        logger.addHandler(daily_handler)

        logger.debug(
            f"Daily rotating file handler configured for '{name}' "
            f"in directory: {log_path}"
        )

    except Exception as e:
        # If file logging fails, continue with console only
        logger.warning(f"Could not configure file logging: {e.__class__.__name__}: {e}")
        logger.warning("Logging will continue to console only")

    return logger


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger wrapper for the given logger name.

    This function returns a StructuredLogger that wraps the underlying logger,
    adding support for structured logging with context fields.

    Args:
        name: Logger name (application name)

    Returns:
        StructuredLogger: Wrapper with structured logging capabilities

    Usage:
        >>> structured = get_structured_logger("template_api")
        >>> structured.set_context(request_id="abc123")
        >>> structured.info("Processing request", user_id=456)
        >>> # Output includes: request_id=abc123 user_id=456
    """
    logger = get_logger(name)
    return StructuredLogger(logger)


@contextmanager
def log_performance(
    logger: logging.Logger,
    operation: str,
    threshold_ms: float = 1000.0,
    log_args: bool = False,
    **context_fields,
):
    """
    Context manager to measure and log operation execution time.

    This utility helps identify performance bottlenecks by automatically
    logging operation duration. Logs at WARNING level if operation exceeds
    threshold, otherwise logs at DEBUG level.

    Args:
        logger: Logger instance to use
        operation: Descriptive name of the operation being measured
        threshold_ms: Threshold in milliseconds for slow operation warning
        log_args: If True, includes context_fields in log output
        **context_fields: Additional context to include in logs

    Yields:
        None

    Usage:
        >>> with log_performance(logger, "Database query", threshold_ms=500):
        ...     result = await db.execute(query)
        >>> # Logs: "Database query completed in 234.56ms"

        >>> with log_performance(logger, "API call", log_args=True, user_id=123):
        ...     response = await api_client.get(url)
        >>> # Logs: "API call completed in 1234.56ms | user_id=123"

    Log Output:
        - DEBUG: If operation completes within threshold
        - WARNING: If operation exceeds threshold (potential performance issue)
        - ERROR: If operation fails (includes timing and exception info)
    """
    start = time.perf_counter()
    context_str = ""
    if log_args and context_fields:
        context_str = " | " + " ".join(f"{k}={v}" for k, v in context_fields.items())

    try:
        yield
    except Exception:
        # Log exception with timing info before re-raising
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.error(
            f"{operation} FAILED after {elapsed_ms:.2f}ms{context_str}",
            exc_info=True,
        )
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms >= threshold_ms:
            logger.warning(
                f"{operation} took {elapsed_ms:.2f}ms "
                f"(SLOW - threshold: {threshold_ms}ms){context_str}"
            )
        else:
            logger.debug(f"{operation} completed in {elapsed_ms:.2f}ms{context_str}")


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default configuration.

    This is a convenience function that returns an existing logger if available,
    or creates a new one using setup_logger() with default settings.

    IMPORTANT: For application code, prefer explicit setup:
        1. Call setup_logger() ONCE in main.py or config/logger.py
        2. Import that logger instance in all other modules

    This function is mainly for internal use by repositorio_lib or when you
    need a quick logger with defaults.

    Args:
        name: Logger name (application name)

    Returns:
        logging.Logger: Configured logger instance

    Usage:
        >>> # Internal library use:
        >>> logger = get_logger("repositorio")
        >>> logger.info("Library operation")

        >>> # Application use (preferred pattern):
        >>> # In config/logger.py:
        >>> logger = setup_logger("myapp", level=logging.INFO)
        >>> # In other modules:
        >>> from config.logger import logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Logger not configured yet - set it up with defaults
        return setup_logger(name)
    return logger
