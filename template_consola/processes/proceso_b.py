"""
Process B - Independent Worker

Example process that runs in parallel with other processes.
Simulates a report generation process.
"""

import asyncio
from datetime import datetime

# Centralized loggers
from config.logger import logger, structured_logger


async def ejecutar_proceso_b():
    """
    Process B: Simulates periodic report generation.

    This process:
    1. Collects data from multiple sources
    2. Generates statistics
    3. Creates report file
    4. Sends notifications
    """
    logger.info("🟢 [PROCESS B] Starting...")

    try:
        start_time = datetime.now()

        # Set context for this process
        structured_logger.set_context(
            process_name="Process B",
            execution_date=start_time.isoformat()
        )

        structured_logger.info("Process B started", event_type="process_start")

        # Simulate data collection
        logger.info("🟢 [PROCESS B] Collecting data for report...")
        await asyncio.sleep(1.5)

        # Simulate statistics generation
        logger.info("🟢 [PROCESS B] Calculating statistics...")
        await asyncio.sleep(2)

        # Simulate file creation
        logger.info("🟢 [PROCESS B] Generating report file (PDF)...")
        await asyncio.sleep(1.5)

        # Simulate sending
        logger.info("🟢 [PROCESS B] Sending report via email...")
        await asyncio.sleep(1)

        # Complete - log with metrics
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("✅ [PROCESS B] Completed successfully - Report generated and sent")

        structured_logger.info(
            "Process B completed successfully",
            report_generated=True,
            report_sent=True,
            duration_seconds=round(duration, 2),
            status="success",
            event_type="process_completed"
        )
        structured_logger.clear_context()

    except Exception as e:
        logger.error(f"❌ [PROCESS B] Error: {e}", exc_info=True)

        # Log error with structured logger
        structured_logger.error(
            "Process B failed",
            error=str(e),
            status="error",
            event_type="process_error"
        )
        structured_logger.clear_context()

        raise
