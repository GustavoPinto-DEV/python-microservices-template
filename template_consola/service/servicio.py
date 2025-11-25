"""
Main Service

Orchestrates the execution of console batch processes.
Manages the service lifecycle and coordinates tasks.
"""

import asyncio
from datetime import datetime
import os

# Centralized loggers
from config.logger import logger, structured_logger

# Processes
from processes.ejemplo_proceso import execute_example_process
from processes.proceso_a import execute_process_a
from processes.proceso_b import execute_process_b
from processes.proceso_c import execute_process_c

# TODO: Uncomment when you have repositorio_lib
# from repositorio_lib.utils import retry_until_success


class Service:
    """
    Main console service.

    Manages:
    - Service start and stop
    - Periodic process execution
    - Error handling and retries
    """

    def __init__(self):
        """Initializes the service"""
        self.running = False
        self.task = None

        # Configuration from env
        self.interval_minutes = int(os.getenv("MINUTOS_CONSOLA", "60"))
        self.continuous_mode = os.getenv("ENABLE_CONTINUOUS_MODE", "true").lower() == "true"
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))

        logger.info(f"Service configured:")
        logger.info(f"  - Interval: {self.interval_minutes} minutes")
        logger.info(f"  - Continuous mode: {self.continuous_mode}")
        logger.info(f"  - Max retries: {self.max_retries}")

    async def start_service(self):
        """
        Starts the service and begins process execution.
        """
        logger.info("🟢 Starting service...")

        self.running = True

        # Start main task in background
        self.task = asyncio.create_task(self._run_loop())

        logger.info("✅ Service started successfully")

    async def stop_service(self):
        """
        Stops the service gracefully.
        """
        logger.info("🔴 Stopping service...")

        self.running = False

        # Wait for current task to finish
        if self.task:
            try:
                await asyncio.wait_for(self.task, timeout=60)
                logger.info("✅ Current task completed")
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout waiting for task, canceling...")
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass

        logger.info("✅ Service stopped")

    async def _run_loop(self):
        """
        Main service loop.

        Executes batch processes periodically according to configuration.
        """
        cycle = 1

        while self.running:
            try:
                logger.info(f"{'='*60}")
                logger.info(f"Starting cycle #{cycle} - {datetime.now()}")
                logger.info(f"{'='*60}")

                # Set context for this cycle execution
                cycle_start = datetime.now()
                structured_logger.set_context(
                    cycle_number=cycle,
                    execution_date=cycle_start.isoformat(),
                    service="template_consola"
                )

                # Execute process cycle
                await self.execute_cycle()

                # Log cycle completion with metrics
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                structured_logger.info(
                    "Cycle completed successfully",
                    cycle_number=cycle,
                    duration_seconds=cycle_duration,
                    event_type="cycle_completed"
                )
                structured_logger.clear_context()

                logger.info(f"✅ Cycle #{cycle} completed successfully")

                # If not continuous mode, exit after first cycle
                if not self.continuous_mode:
                    logger.info("Single execution mode - terminating")
                    self.running = False
                    break

                # Wait before next cycle
                if self.running:
                    logger.info(
                        f"⏳ Waiting {self.interval_minutes} minutes "
                        f"until next cycle..."
                    )
                    await asyncio.sleep(self.interval_minutes * 60)

                cycle += 1

            except asyncio.CancelledError:
                logger.info("⚠️ Task canceled")
                break
            except Exception as e:
                logger.error(
                    f"❌ Error in cycle #{cycle}: {e}",
                    exc_info=True
                )

                # Wait before retrying
                if self.running:
                    logger.info("⏳ Waiting 5 minutes before retrying...")
                    await asyncio.sleep(300)  # 5 minutes

    async def execute_cycle(self):
        """
        Executes a complete batch process cycle.

        Customize this method to add your specific processes.
        """
        logger.info("🔄 Executing cycle processes...")

        try:
            # TODO: Add your processes here

            # ====================================================================
            # OPTION 1: PROCESSES IN SEQUENCE (one after the other)
            # ====================================================================
            # await self._execute_with_retries(execute_example_process, "Example Process")
            # await self._execute_with_retries(execute_process_a, "Process A")
            # await self._execute_with_retries(execute_process_b, "Process B")
            # await self._execute_with_retries(execute_process_c, "Process C")

            # ====================================================================
            # OPTION 2: PROCESSES IN PARALLEL (all at the same time)
            # ====================================================================
            logger.info("⚡ Executing 3 processes in parallel...")

            results = await asyncio.gather(
                self._execute_with_retries(execute_process_a, "Process A"),
                self._execute_with_retries(execute_process_b, "Process B"),
                self._execute_with_retries(execute_process_c, "Process C"),
                return_exceptions=True  # Don't stop if one fails
            )

            # Check results
            errors = [r for r in results if isinstance(r, Exception)]
            successful_count = len(results) - len(errors)

            if errors:
                logger.warning(f"⚠️ {len(errors)} process(es) failed")
                for error in errors:
                    logger.error(f"   - {error}")

                # Log with structured logger for monitoring
                structured_logger.warning(
                    "Parallel processes completed with errors",
                    total_processes=len(results),
                    successful=successful_count,
                    failed=len(errors),
                    event_type="parallel_execution"
                )
            else:
                logger.info("✅ All parallel processes completed successfully")
                structured_logger.info(
                    "All parallel processes completed",
                    total_processes=len(results),
                    successful=successful_count,
                    event_type="parallel_execution"
                )

            # ====================================================================
            # OPTION 3: COMBINATION (some parallel, others sequential)
            # ====================================================================
            # # First execute example process (sequential)
            # await self._execute_with_retries(execute_example_process, "Example Process")
            #
            # # Then execute A, B and C in parallel
            # await asyncio.gather(
            #     self._execute_with_retries(execute_process_a, "Process A"),
            #     self._execute_with_retries(execute_process_b, "Process B"),
            #     self._execute_with_retries(execute_process_c, "Process C"),
            #     return_exceptions=True
            # )

            logger.info("✅ All processes completed")

        except Exception as e:
            logger.error(f"❌ Error executing cycle: {e}", exc_info=True)
            raise

    async def _execute_with_retries(self, function, name: str):
        """
        Executes a function with automatic retries on error.

        Args:
            function: Async function to execute
            name: Descriptive process name
        """
        process_start = datetime.now()

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"▶️ Executing: {name} (attempt {attempt}/{self.max_retries})")

                # Log process start with structured logger
                structured_logger.info(
                    "Process started",
                    process_name=name,
                    attempt=attempt,
                    max_attempts=self.max_retries,
                    event_type="process_start"
                )

                await function()

                # Log successful completion with metrics
                duration = (datetime.now() - process_start).total_seconds()
                structured_logger.info(
                    "Process completed successfully",
                    process_name=name,
                    attempt=attempt,
                    duration_seconds=duration,
                    status="success",
                    event_type="process_completed"
                )

                logger.info(f"✅ {name} completed successfully")
                return

            except Exception as e:
                logger.error(
                    f"❌ Error in {name} (attempt {attempt}/{self.max_retries}): {e}",
                    exc_info=True
                )

                # Log failure with structured logger
                structured_logger.error(
                    "Process execution failed",
                    process_name=name,
                    attempt=attempt,
                    max_attempts=self.max_retries,
                    error=str(e),
                    status="failed",
                    event_type="process_failed"
                )

                if attempt < self.max_retries:
                    # Exponential backoff: 5s, 10s, 20s
                    delay = 5 * (2 ** (attempt - 1))
                    logger.info(f"⏳ Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ {name} failed after {self.max_retries} attempts")

                    # Log final failure
                    duration = (datetime.now() - process_start).total_seconds()
                    structured_logger.error(
                        "Process failed after all retries",
                        process_name=name,
                        total_attempts=self.max_retries,
                        duration_seconds=duration,
                        error=str(e),
                        status="failed_permanently",
                        event_type="process_failed_permanently"
                    )
                    raise


# TODO: Add additional functionality as needed
# Examples:
# - Health check endpoint (simple HTTP server)
# - Execution metrics
# - Email/slack notifications on error
# - Pause/resume service dynamically
# - Adjust interval dynamically
