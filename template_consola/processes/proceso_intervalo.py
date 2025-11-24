"""
Process with Interval-based Execution

Trigger: Every X seconds/minutes (configured via environment variable)
Strategy: Continuous loop with sleep between executions
Use: Tasks that should run periodically without specific schedule
"""

import asyncio
from datetime import datetime

# Centralized logger
from config.logger import logger


async def ejecutar_proceso_intervalo():
    """
    Process that simulates interval-based task execution.

    Real-world examples:
    - Data synchronization from external API
    - Cache updates
    - Service health checks
    - Temporary file cleanup
    """
    logger.info("⏱️ [INTERVAL PROCESS] Starting interval execution...")

    try:
        # Simulate timestamp retrieval
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"⏱️ [INTERVAL PROCESS] Executing at {now}")

        # Simulate processing
        logger.info("⏱️ [INTERVAL PROCESS] Checking external services...")
        await asyncio.sleep(0.5)

        logger.info("⏱️ [INTERVAL PROCESS] Synchronizing data...")
        await asyncio.sleep(0.5)

        logger.info("⏱️ [INTERVAL PROCESS] Updating cache...")
        await asyncio.sleep(0.5)

        # Complete
        logger.info(f"✅ [INTERVAL PROCESS] Completed - Next execution per configured interval")

    except Exception as e:
        logger.error(f"❌ [INTERVAL PROCESS] Error: {e}", exc_info=True)
        raise
