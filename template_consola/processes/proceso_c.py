"""
Process C - Independent Worker

Example process that runs in parallel with other processes.
Simulates a cleanup and maintenance process.
"""

import asyncio
from datetime import datetime

# Centralized loggers
from config.logger import logger, structured_logger


async def ejecutar_proceso_c():
    """
    Process C: Simulates cleanup and maintenance tasks.

    This process:
    1. Deletes old records
    2. Cleans temporary files
    3. Optimizes database indexes
    4. Generates maintenance logs
    """
    logger.info("🟡 [PROCESS C] Starting...")

    try:
        start_time = datetime.now()

        # Set context for this process
        structured_logger.set_context(
            process_name="Process C",
            execution_date=start_time.isoformat()
        )

        structured_logger.info("Process C started", event_type="process_start")

        # Simulate record cleanup
        logger.info("🟡 [PROCESS C] Deleting old records (>90 days)...")
        await asyncio.sleep(2)
        deleted_records = 342
        logger.info(f"🟡 [PROCESS C] {deleted_records} records deleted")

        # Simulate file cleanup
        logger.info("🟡 [PROCESS C] Cleaning temporary files...")
        await asyncio.sleep(1)

        # Simulate DB optimization
        logger.info("🟡 [PROCESS C] Optimizing database indexes...")
        await asyncio.sleep(2.5)

        # Simulate log generation
        logger.info("🟡 [PROCESS C] Generating maintenance log...")
        await asyncio.sleep(0.5)

        # Complete - log with metrics
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [PROCESS C] Completed successfully - {deleted_records} records cleaned")

        structured_logger.info(
            "Process C completed successfully",
            records_deleted=deleted_records,
            cleanup_tasks_completed=4,
            duration_seconds=round(duration, 2),
            status="success",
            event_type="process_completed"
        )
        structured_logger.clear_context()

    except Exception as e:
        logger.error(f"❌ [PROCESS C] Error: {e}", exc_info=True)

        # Log error with structured logger
        structured_logger.error(
            "Process C failed",
            error=str(e),
            status="error",
            event_type="process_error"
        )
        structured_logger.clear_context()

        raise
