"""
Project-specific Utilities for Console

Helper functions and utilities specific to this console service.
For utilities shared between projects, use repositorio_lib/utils/
"""

import asyncio
from typing import Optional, Callable, Any
from datetime import datetime
import httpx

from config.logger import logger


async def retry_operation(
    function: Callable,
    max_attempts: int = 3,
    initial_delay: int = 5,
    name: str = "Operation"
) -> Any:
    """
    Executes a function with automatic retries and exponential backoff.

    Args:
        function: Async function to execute
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        name: Descriptive name for logging

    Returns:
        Function result

    Raises:
        Exception: If all attempts fail
    """
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Executing {name} (attempt {attempt}/{max_attempts})")
            result = await function()
            logger.info(f"✅ {name} successful")
            return result

        except Exception as e:
            logger.error(f"❌ Error in {name} (attempt {attempt}): {e}")

            if attempt < max_attempts:
                # Exponential backoff
                delay = initial_delay * (2 ** (attempt - 1))
                logger.info(f"⏳ Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"❌ {name} failed after {max_attempts} attempts")
                raise


async def call_external_api(
    url: str,
    method: str = "GET",
    headers: Optional[dict] = None,
    data: Optional[dict] = None,
    timeout: int = 30,
    retry: bool = True
) -> Optional[dict]:
    """
    Makes call to external API with error handling and retries.

    Args:
        url: API URL
        method: HTTP method
        headers: HTTP headers
        data: Data for POST/PUT
        timeout: Timeout in seconds
        retry: Whether to retry on error

    Returns:
        Response JSON or None if error
    """
    async def _make_call():
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

    try:
        if retry:
            return await retry_operation(
                _make_call,
                max_attempts=3,
                name=f"API {method} {url}"
            )
        else:
            return await _make_call()

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {url}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Connection error: {url} - {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling API: {e}", exc_info=True)
        return None


def format_duration(seconds: float) -> str:
    """
    Formats duration in readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 30m 15s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"

    hours = int(minutes // 60)
    remaining_minutes = minutes % 60

    return f"{hours}h {remaining_minutes}m"


def calculate_next_execution(interval_minutes: int) -> datetime:
    """
    Calculates the time of next execution.

    Args:
        interval_minutes: Interval in minutes

    Returns:
        Datetime of next execution
    """
    from datetime import timedelta
    return datetime.now() + timedelta(minutes=interval_minutes)


async def process_in_batches(
    items: list,
    processing_function: Callable,
    batch_size: int = 10,
    parallel: bool = False
) -> tuple[int, int]:
    """
    Processes a list of items in batches.

    Args:
        items: List of items to process
        processing_function: Async function that processes each item
        batch_size: Batch size
        parallel: If True, processes items in parallel within each batch

    Returns:
        Tuple (successful, failed)
    """
    successful = 0
    failed = 0
    total = len(items)

    for i in range(0, total, batch_size):
        batch = items[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} items)")

        if parallel:
            # Process in parallel
            tasks = [processing_function(item) for item in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    failed += 1
                else:
                    successful += 1
        else:
            # Process sequentially
            for item in batch:
                try:
                    await processing_function(item)
                    successful += 1
                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    failed += 1

        logger.info(f"Batch completed: {successful} ok, {failed} errors")

    return successful, failed


def create_execution_report(
    start: datetime,
    end: datetime,
    records_processed: int,
    successful: int,
    failed: int,
    errors: list = None
) -> dict:
    """
    Creates a structured execution report.

    Args:
        start: Start timestamp
        end: End timestamp
        records_processed: Total records processed
        successful: Number of successful
        failed: Number of failed
        errors: List of errors that occurred

    Returns:
        Dictionary with report
    """
    duration = (end - start).total_seconds()

    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "duration_seconds": duration,
        "formatted_duration": format_duration(duration),
        "records_processed": records_processed,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / records_processed * 100) if records_processed > 0 else 0,
        "errors": errors or []
    }


async def send_notification(
    title: str,
    message: str,
    level: str = "info",
    destinations: list = None
):
    """
    Sends notifications through different channels.

    Args:
        title: Notification title
        message: Message content
        level: Severity level (info, warning, error)
        destinations: List of destinations (email, slack, etc.)

    TODO: Implement real notification channels
    """
    logger.info(f"📧 Notification [{level}]: {title} - {message}")

    # TODO: Implement real sending
    # if "email" in destinations:
    #     await send_email(title, message)
    # if "slack" in destinations:
    #     await send_slack(title, message)


# TODO: Add more utilities as needed for the project
# Examples:
# - Specific validations
# - Data parsers
# - SFTP helpers
# - File generators (CSV, Excel, PDF)
# - Compression/decompression
