"""
Console Template - Main Entry Point

Template for console/batch services based on asyncio.
Executes background processes continuously or on schedule.

Usage:
    python main.py
"""

import asyncio
import signal
import logging

# Centralized logger (ONE SINGLE logger for the entire application)
from config.logger import logger

# Service
from service.servicio import Service


async def main():
    """
    Main console function.

    Background service that executes batch processes continuously:
    - Automatic data updates
    - Processing of pending tasks
    - Synchronization with external systems
    - Report generation
    """
    logger.info("🚀 Starting console service...")

    # Initialize service
    service = Service()
    await service.start_service()

    # region Signal Handling
    # Handle termination signals for graceful shutdown
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
    # endregion

    logger.info("✅ Service running. Press Ctrl+C to stop")

    try:
        # Wait for stop signal
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("⌨️ Keyboard interrupt received")

    # Stop service cleanly
    await service.stop_service()
    logger.info("🛑 Console service terminated")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal application error: {e}", exc_info=True)
        exit(1)
