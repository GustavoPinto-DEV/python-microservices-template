"""
Process B - Independent Worker

Example process that runs in parallel with other processes.
Simulates a report generation process.
"""

import asyncio
from datetime import datetime

# Centralized logger
from config.logger import logger


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

        # Complete
        logger.info("✅ [PROCESS B] Completed successfully - Report generated and sent")

    except Exception as e:
        logger.error(f"❌ [PROCESS B] Error: {e}", exc_info=True)
        raise
