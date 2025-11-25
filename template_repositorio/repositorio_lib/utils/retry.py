"""
Retry Logic - Utilities for retries with exponential backoff

Decorators and functions to handle retries in asynchronous operations.
"""

import asyncio
import functools
import time
from typing import Any, Callable, Optional, Tuple, Type

# Direct imports to avoid circular dependency
from repositorio_lib.core import log_performance
from repositorio_lib.config import logger


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator to retry synchronous functions with exponential backoff.

    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplication factor for each retry
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch

    Usage:
        @retry_with_exponential_backoff(max_retries=5)
        def my_function():
            # code that may fail
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {e}",
                            exc_info=True,
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

        return wrapper

    return decorator


def retry_async(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator to retry async functions with exponential backoff.

    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplication factor for each retry
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch

    Usage:
        @retry_async(max_retries=5)
        async def my_async_function():
            # async code that may fail
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            func_name = func.__name__

            with log_performance(
                logger, f"Retry wrapper: {func_name}", threshold_ms=10000
            ):
                for attempt in range(max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_retries:
                            logger.error(
                                f"{func_name} failed after {max_retries} retries: {e}",
                                exc_info=True,
                            )
                            raise

                        logger.warning(
                            f"{func_name} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                        await asyncio.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)

        return wrapper

    return decorator


async def retry_until_success(
    func: Callable,
    max_attempts: int = 3,
    delay: float = 1.0,
    name: Optional[str] = None,
) -> Any:
    """
    Execute a function until it succeeds or max attempts are exhausted.

    Args:
        func: Function to execute (can be async or sync)
        max_attempts: Maximum number of attempts
        delay: Seconds between attempts
        name: Descriptive name for logs

    Returns:
        Any: Result of the function

    Raises:
        Exception: If max attempts are exhausted

    Note:
        For sync functions, consider using retry_with_exponential_backoff decorator instead.
        This function is primarily designed for async operations.
    """
    func_name = name or getattr(func, "__name__", "unknown_function")
    is_async = asyncio.iscoroutinefunction(func)

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Executing {func_name} (attempt {attempt}/{max_attempts})")

            if is_async:
                result = await func()
            else:
                result = func()

            logger.info(f"{func_name} executed successfully")
            return result

        except Exception as e:
            logger.error(
                f"Error in {func_name} (attempt {attempt}/{max_attempts}): {e}",
                exc_info=True,
            )

            if attempt < max_attempts:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"{func_name} failed after {max_attempts} attempts")
                raise


def retry_sync_until_success(
    func: Callable,
    max_attempts: int = 3,
    delay: float = 1.0,
    name: Optional[str] = None,
) -> Any:
    """
    Execute a synchronous function until it succeeds or max attempts are exhausted.

    Args:
        func: Synchronous function to execute
        max_attempts: Maximum number of attempts
        delay: Seconds between attempts
        name: Descriptive name for logs

    Returns:
        Any: Result of the function

    Raises:
        Exception: If max attempts are exhausted
    """
    func_name = name or getattr(func, "__name__", "unknown_function")

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Executing {func_name} (attempt {attempt}/{max_attempts})")
            result = func()
            logger.info(f"{func_name} executed successfully")
            return result

        except Exception as e:
            logger.error(
                f"Error in {func_name} (attempt {attempt}/{max_attempts}): {e}",
                exc_info=True,
            )

            if attempt < max_attempts:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"{func_name} failed after {max_attempts} attempts")
                raise
