"""
Main with Advanced Scheduler

Alternative entry point that uses SchedulerService
to execute multiple processes with different triggers.

Usage:
    python main_scheduler.py              # Production mode with all schedulers
    python main_scheduler.py --test       # Test mode (executes all once)
    python main_scheduler.py --process=interval  # Execute specific process
"""

import asyncio
import signal
import logging
import sys

# Centralized logger (ONE SINGLE logger for the entire application)
from config.logger import logger

# Service
from service.servicio_scheduler import SchedulerService, test_all_processes


async def main():
    """
    Main function with advanced scheduler.
    """
    # Parse simple arguments
    test_mode = "--test" in sys.argv
    manual_process = None

    for arg in sys.argv:
        if arg.startswith("--process="):
            manual_process = arg.split("=")[1]

    # ========================================================================
    # TEST MODE: Execute all processes once
    # ========================================================================
    if test_mode:
        logger.info("🧪 TEST MODE ACTIVATED")
        await test_all_processes()
        return

    # ========================================================================
    # MANUAL MODE: Execute a specific process
    # ========================================================================
    if manual_process:
        logger.info(f"🎯 MANUAL MODE: Executing process '{manual_process}'")
        service = SchedulerService()
        await service.execute_manual_process(manual_process)
        return

    # ========================================================================
    # PRODUCTION MODE: Start all schedulers
    # ========================================================================
    logger.info("🚀 Starting service with multiple schedulers...")

    # Initialize service
    service = SchedulerService()
    await service.start_service()

    # Signal handling for graceful shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def stop():
        """Callback to stop the service"""
        logger.info("⚠️ Stop signal received")
        stop_event.set()

    try:
        # Register handlers for SIGINT (Ctrl+C) and SIGTERM (docker stop)
        loop.add_signal_handler(signal.SIGINT, stop)
        loop.add_signal_handler(signal.SIGTERM, stop)
        logger.info("✅ Signal handlers registered")
    except NotImplementedError:
        # Windows doesn't support add_signal_handler
        logger.warning(
            "⚠️ Signals not supported on this platform. "
            "Use Ctrl+C to exit."
        )

    logger.info("✅ Service running with multiple schedulers")
    logger.info("💡 Press Ctrl+C to stop")
    logger.info("")
    logger.info("📊 ACTIVE PROCESSES:")
    logger.info("   1. Interval Process       → Every 5 minutes")
    logger.info("   2. Fixed Time Process     → Daily at 03:00 AM")
    logger.info("   3. Specific Days Process  → Mon, Wed, Fri at 06:30 AM")
    logger.info("   4. Cron Process           → Every 4 hours (0 */4 * * *)")
    logger.info("   5. Continuous Process     → Permanent loop (every 10s)")
    logger.info("   6. Event Monitor          → Listens for external triggers")
    logger.info("")

    try:
        # Wait for stop signal
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("⌨️ Keyboard interrupt received")

    # Stop service cleanly
    await service.stop_service()
    logger.info("🛑 Scheduler service terminated")


if __name__ == "__main__":
    logger.info("="*70)
    logger.info("  CONSOLE SERVICE - ADVANCED SCHEDULER")
    logger.info("="*70)
    logger.info("")

    # Show usage if --help is passed
    if "--help" in sys.argv or "-h" in sys.argv:
        print("\nUsage:")
        print("  python main_scheduler.py                    # Production mode")
        print("  python main_scheduler.py --test             # Test mode")
        print("  python main_scheduler.py --process=interval # Execute specific process")
        print("\nAvailable processes:")
        print("  - interval")
        print("  - fixed_time")
        print("  - specific_days")
        print("  - cron")
        print("  - event")
        print("  - continuous")
        print("")
        sys.exit(0)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal application error: {e}", exc_info=True)
        exit(1)
