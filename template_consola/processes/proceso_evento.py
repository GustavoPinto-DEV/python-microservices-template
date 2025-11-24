"""
Process with Event Trigger

Trigger: External event (file in folder, DB flag, signal)
Strategy: Watchdog + file system monitoring or flag polling
Use: Reactive tasks that respond to specific events
"""

import asyncio
from datetime import datetime
from pathlib import Path

# Centralized logger
from config.logger import logger


async def ejecutar_proceso_evento(trigger_info: str = "manual"):
    """
    Process that simulates task executed by external event.

    Real-world examples:
    - Processing file uploaded to folder
    - Flag activated in database
    - Message received in queue (RabbitMQ, Redis)
    - Webhook received
    - Change detected in configuration file

    Args:
        trigger_info: Information about the trigger that activated the process
    """
    logger.info("🎯 [EVENT PROCESS] Trigger detected - Starting execution...")

    try:
        # Trigger information
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"🎯 [EVENT PROCESS] Executing at {now}")
        logger.info(f"🎯 [EVENT PROCESS] Trigger: {trigger_info}")

        # Simulate trigger verification
        logger.info("🎯 [EVENT PROCESS] Verifying trigger event...")
        await asyncio.sleep(0.3)

        # Simulate different event types
        if "archivo" in trigger_info.lower() or "file" in trigger_info.lower():
            logger.info("📁 [EVENT PROCESS] Type: File detected")
            logger.info("📁 [EVENT PROCESS] Processing file...")
            await asyncio.sleep(1.5)
            logger.info("📁 [EVENT PROCESS] File processed and moved to 'processed/'")

        elif "flag" in trigger_info.lower() or "bd" in trigger_info.lower() or "db" in trigger_info.lower():
            logger.info("🏁 [EVENT PROCESS] Type: Database flag")
            logger.info("🏁 [EVENT PROCESS] Querying pending records...")
            await asyncio.sleep(1)
            logger.info("🏁 [EVENT PROCESS] Processing record batch...")
            await asyncio.sleep(1.5)
            logger.info("🏁 [EVENT PROCESS] Flag updated to 'processed'")

        elif "webhook" in trigger_info.lower():
            logger.info("🌐 [EVENT PROCESS] Type: Webhook received")
            logger.info("🌐 [EVENT PROCESS] Validating payload...")
            await asyncio.sleep(0.5)
            logger.info("🌐 [EVENT PROCESS] Executing requested action...")
            await asyncio.sleep(1)
            logger.info("🌐 [EVENT PROCESS] Responding to source...")
            await asyncio.sleep(0.3)

        else:
            logger.info("⚡ [EVENT PROCESS] Type: Generic event")
            logger.info("⚡ [EVENT PROCESS] Processing event...")
            await asyncio.sleep(1)

        # Results
        response_time_ms = 250

        logger.info(f"📊 [EVENT PROCESS] Metrics:")
        logger.info(f"   - Response time: {response_time_ms}ms")
        logger.info(f"   - Trigger: {trigger_info}")
        logger.info(f"   - Status: Waiting for next event")

        logger.info(f"✅ [EVENT PROCESS] Completed - Waiting for next event")

    except Exception as e:
        logger.error(f"❌ [EVENT PROCESS] Error: {e}", exc_info=True)
        raise


async def monitorear_eventos():
    """
    Auxiliary function to monitor events continuously.

    This function would run in a separate loop monitoring:
    - File system (watchdog)
    - Database (polling)
    - Message queue (subscriber)
    - API endpoints (webhooks)
    """
    logger.info("👁️ [EVENT MONITOR] Starting event monitoring...")

    # Simulate monitor configuration
    await asyncio.sleep(0.5)

    logger.info("👁️ [EVENT MONITOR] Monitoring:")
    logger.info("   - Folder: ./data/inbox/")
    logger.info("   - DB Flags: table 'pending_tasks'")
    logger.info("   - Webhooks: /api/trigger")
    logger.info("👁️ [EVENT MONITOR] Event system active")
