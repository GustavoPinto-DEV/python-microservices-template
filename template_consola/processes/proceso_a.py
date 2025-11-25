"""
Process A - Independent Worker

Example process that runs in parallel with other processes.
Simulates a data update process.
"""

import asyncio
from datetime import datetime

# Centralized loggers
from config.logger import logger, structured_logger


async def ejecutar_proceso_a():
    """
    Process A: Simulates data update from external source.

    This process:
    1. Connects to a data source (simulated)
    2. Downloads updated information
    3. Processes and validates the data
    4. Updates the database
    """
    logger.info("🔵 [PROCESS A] Starting...")

    try:
        start_time = datetime.now()

        # Set context for this process
        structured_logger.set_context(
            process_name="Process A",
            execution_date=start_time.isoformat()
        )

        structured_logger.info("Process A started", event_type="process_start")

        # Simulate process start
        logger.info("🔵 [PROCESS A] Connecting to data source...")
        await asyncio.sleep(1)

        # Simulate data download
        logger.info("🔵 [PROCESS A] Downloading information...")
        await asyncio.sleep(2)

        # Simulate processing
        processed_records = 150
        logger.info(f"🔵 [PROCESS A] Processing {processed_records} records...")
        await asyncio.sleep(1.5)

        # Simulate DB update
        logger.info("🔵 [PROCESS A] Updating database...")
        await asyncio.sleep(1)

        # Complete - log with metrics
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [PROCESS A] Completed successfully - {processed_records} records updated")

        structured_logger.info(
            "Process A completed successfully",
            records_updated=processed_records,
            duration_seconds=round(duration, 2),
            status="success",
            event_type="process_completed"
        )
        structured_logger.clear_context()

    except Exception as e:
        logger.error(f"❌ [PROCESS A] Error: {e}", exc_info=True)

        # Log error with structured logger
        structured_logger.error(
            "Process A failed",
            error=str(e),
            status="error",
            event_type="process_error"
        )
        structured_logger.clear_context()

        raise
