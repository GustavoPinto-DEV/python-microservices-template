"""
Process with Continuous Loop

Trigger: Permanent execution with small pauses between iterations
Strategy: Infinite while loop with asyncio.sleep
Use: Constant monitoring, queue processing, permanent workers
"""

import asyncio
from datetime import datetime
import random

# Centralized logger
from config.logger import logger


# Global variable to control the loop
_running = True


async def ejecutar_proceso_continuo():
    """
    Process that simulates permanent worker running continuously.

    Real-world examples:
    - Message queue worker (RabbitMQ, Redis)
    - Real-time service monitor
    - Data stream processor
    - Event consumer
    - Permanent health checker
    """
    logger.info("♾️ [CONTINUOUS PROCESS] Starting permanent worker...")

    iteration = 0

    try:
        while _running:
            iteration += 1
            now = datetime.now().strftime("%H:%M:%S")

            # Log every 10 iterations to avoid saturation
            if iteration % 10 == 1:
                logger.info(f"♾️ [CONTINUOUS PROCESS] Iteration #{iteration} - {now}")

            # Simulate queue check
            pending_tasks = random.randint(0, 5)

            if pending_tasks > 0:
                logger.info(f"♾️ [CONTINUOUS PROCESS] {pending_tasks} task(s) found")

                for i in range(pending_tasks):
                    logger.info(f"♾️ [CONTINUOUS PROCESS] Processing task {i+1}/{pending_tasks}...")
                    # Simulate processing
                    await asyncio.sleep(0.5)
                    logger.info(f"✅ [CONTINUOUS PROCESS] Task {i+1} completed")

            # Small pause before next iteration
            await asyncio.sleep(3)  # 3 seconds between checks

            # For demo purposes, stop after 5 iterations
            # In production, this would run indefinitely
            if iteration >= 5:
                logger.info("♾️ [CONTINUOUS PROCESS] Demo completed (5 iterations)")
                logger.info("♾️ [CONTINUOUS PROCESS] In production, this would run indefinitely")
                break

        logger.info(f"✅ [CONTINUOUS PROCESS] Worker stopped after {iteration} iterations")

    except asyncio.CancelledError:
        logger.info("⚠️ [CONTINUOUS PROCESS] Worker cancelled - stopping gracefully")
        raise
    except Exception as e:
        logger.error(f"❌ [CONTINUOUS PROCESS] Error: {e}", exc_info=True)
        raise


def detener_proceso_continuo():
    """Function to stop continuous process externally"""
    global _running
    _running = False
    logger.info("🛑 [CONTINUOUS PROCESS] Stop signal received")


async def ejecutar_proceso_continuo_iteracion():
    """
    Alternative version: Executes a single iteration of the continuous process.
    Useful for testing or when you want to control the loop externally.
    """
    logger.info("♾️ [CONTINUOUS PROCESS] Executing one iteration...")

    try:
        # Simulate queue check
        pending_tasks = random.randint(0, 3)

        if pending_tasks > 0:
            logger.info(f"♾️ [CONTINUOUS PROCESS] {pending_tasks} task(s) in queue")

            for i in range(pending_tasks):
                logger.info(f"♾️ [CONTINUOUS PROCESS] Processing task {i+1}...")
                await asyncio.sleep(0.3)
        else:
            logger.info("♾️ [CONTINUOUS PROCESS] Empty queue - waiting...")

        logger.info("✅ [CONTINUOUS PROCESS] Iteration completed")

    except Exception as e:
        logger.error(f"❌ [CONTINUOUS PROCESS] Error: {e}", exc_info=True)
        raise
