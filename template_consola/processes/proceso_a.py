"""
Process A - Independent Worker

Example process that runs in parallel with other processes.
Simulates a data update process.
"""

import asyncio
from datetime import datetime

# Centralized logger
from config.logger import logger


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

        # Complete
        logger.info(f"✅ [PROCESS A] Completed successfully - {processed_records} records updated")

    except Exception as e:
        logger.error(f"❌ [PROCESS A] Error: {e}", exc_info=True)
        raise
