"""
Process with Specific Days Execution

Trigger: Monday, Wednesday and Friday at 06:30 AM
Strategy: APScheduler with CronTrigger and day_of_week
Use: Tasks that should run only on certain days of the week
"""

import asyncio
from datetime import datetime

# Centralized logger
from config.logger import logger


async def ejecutar_proceso_dias_especificos():
    """
    Process that simulates task executed only on certain days.

    Real-world examples:
    - Synchronization with external systems (Mon, Wed, Fri)
    - Specific weekly report generation
    - Data cleanup (only business days)
    - Reminder sending (beginning/middle/end of week)
    - Processes requiring support staff availability
    """
    logger.info("📅 [SPECIFIC DAYS PROCESS] Starting scheduled execution...")

    try:
        # Verify day and time
        now = datetime.now()
        weekday = now.strftime("%A")  # Monday, Tuesday, etc.
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")

        logger.info(f"📅 [SPECIFIC DAYS PROCESS] Today is {weekday}")
        logger.info(f"📅 [SPECIFIC DAYS PROCESS] Executing at {time_str} on {date_str}")

        # Simulate synchronization
        logger.info("📅 [SPECIFIC DAYS PROCESS] Connecting to external system...")
        await asyncio.sleep(1)

        logger.info("📅 [SPECIFIC DAYS PROCESS] Downloading updated data...")
        await asyncio.sleep(1.5)

        logger.info("📅 [SPECIFIC DAYS PROCESS] Processing information...")
        await asyncio.sleep(1)

        logger.info("📅 [SPECIFIC DAYS PROCESS] Updating local database...")
        await asyncio.sleep(0.5)

        # Simulate results
        synchronized_files = 47
        updated_records = 892

        logger.info(f"📊 [SPECIFIC DAYS PROCESS] Results:")
        logger.info(f"   - Synchronized files: {synchronized_files}")
        logger.info(f"   - Updated records: {updated_records}")
        logger.info(f"   - Execution days: Monday, Wednesday, Friday")
        logger.info(f"   - Execution time: 06:30 AM")

        logger.info(f"✅ [SPECIFIC DAYS PROCESS] Completed successfully")

    except Exception as e:
        logger.error(f"❌ [SPECIFIC DAYS PROCESS] Error: {e}", exc_info=True)
        raise
