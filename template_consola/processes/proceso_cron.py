"""
Process with Cron Expression

Trigger: Based on cron expression (e.g., "0 */4 * * *" = every 4 hours)
Strategy: APScheduler with CronTrigger and cron expressions
Use: Complex scheduling with standard cron syntax
"""

import asyncio
from datetime import datetime

# Centralized logger
from config.logger import logger


async def ejecutar_proceso_cron():
    """
    Process that simulates task executed with cron expression.

    Real-world examples:
    - "0 */4 * * *" -> Every 4 hours on the hour
    - "0 9-17 * * MON-FRI" -> Every hour from 9 AM to 5 PM, business days
    - "*/15 * * * *" -> Every 15 minutes
    - "0 2 * * SUN" -> Sundays at 2 AM
    - "0 0 1 * *" -> First day of each month at midnight
    """
    logger.info("⏰ [CRON PROCESS] Starting execution with cron trigger...")

    try:
        # Execution information
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"⏰ [CRON PROCESS] Executing at {timestamp}")
        logger.info(f"⏰ [CRON PROCESS] Cron expression: '0 */4 * * *' (every 4 hours)")

        # Simulate resource check
        logger.info("⏰ [CRON PROCESS] Checking system resources...")
        await asyncio.sleep(0.8)

        cpu_usage = 45.2
        memory_usage = 62.1
        disk_usage = 38.5

        logger.info(f"⏰ [CRON PROCESS] System metrics:")
        logger.info(f"   - CPU: {cpu_usage}%")
        logger.info(f"   - Memory: {memory_usage}%")
        logger.info(f"   - Disk: {disk_usage}%")

        # Simulate maintenance
        logger.info("⏰ [CRON PROCESS] Running maintenance tasks...")
        await asyncio.sleep(1)

        logger.info("⏰ [CRON PROCESS] Optimizing indexes...")
        await asyncio.sleep(0.7)

        logger.info("⏰ [CRON PROCESS] Cleaning temporary files...")
        await asyncio.sleep(0.5)

        deleted_files = 234
        freed_space_mb = 1024

        logger.info(f"📊 [CRON PROCESS] Summary:")
        logger.info(f"   - Temporary files deleted: {deleted_files}")
        logger.info(f"   - Space freed: {freed_space_mb} MB")
        logger.info(f"   - Next execution: In 4 hours")

        logger.info(f"✅ [CRON PROCESS] Completed successfully")

    except Exception as e:
        logger.error(f"❌ [CRON PROCESS] Error: {e}", exc_info=True)
        raise
