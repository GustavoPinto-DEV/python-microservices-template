"""
Advanced Service with Multiple Schedulers

Orchestrates multiple processes with different scheduling strategies:
- Fixed intervals
- Specific hours
- Specific days and hours
- Cron expressions
- Event triggers
- Continuous loops
"""

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Centralized logger
from config.logger import logger

# Import processes
from processes.proceso_intervalo import ejecutar_proceso_intervalo
from processes.proceso_hora_fija import ejecutar_proceso_hora_fija
from processes.proceso_dias_especificos import ejecutar_proceso_dias_especificos
from processes.proceso_cron import ejecutar_proceso_cron
from processes.proceso_evento import ejecutar_proceso_evento, monitorear_eventos
from processes.proceso_continuo import ejecutar_proceso_continuo_iteracion


class SchedulerService:
    """
    Advanced service that orchestrates multiple processes with different schedulers.

    Features:
    - APScheduler for complex scheduling
    - Multiple parallel triggers
    - Graceful signal handling
    - Event monitoring
    - Continuous workers
    """

    def __init__(self):
        """Initialize the service with scheduler"""
        self.running = False
        self.scheduler = None
        self.continuous_tasks = []

        logger.info("📅 Scheduler Service configured")

    async def start_service(self):
        """
        Start the service and all schedulers.
        """
        logger.info("🟢 Starting Scheduler Service...")

        self.running = True

        # Create and configure scheduler
        self.scheduler = AsyncIOScheduler()

        # ====================================================================
        # 1. INTERVAL PROCESS - Every 5 minutes
        # ====================================================================
        self.scheduler.add_job(
            func=self._execute_with_wrapper(ejecutar_proceso_intervalo, "Interval Process"),
            trigger=IntervalTrigger(minutes=5),
            id="proceso_intervalo",
            name="Interval Process (every 5 min)",
            replace_existing=True
        )
        logger.info("✅ Configured: Interval Process (every 5 minutes)")

        # ====================================================================
        # 2. FIXED TIME PROCESS - Daily at 03:00 AM
        # ====================================================================
        self.scheduler.add_job(
            func=self._execute_with_wrapper(ejecutar_proceso_hora_fija, "Fixed Time Process"),
            trigger=CronTrigger(hour=3, minute=0),
            id="proceso_hora_fija",
            name="Fixed Time Process (03:00 AM daily)",
            replace_existing=True
        )
        logger.info("✅ Configured: Fixed Time Process (03:00 AM daily)")

        # ====================================================================
        # 3. SPECIFIC DAYS PROCESS - Mon, Wed, Fri at 06:30 AM
        # ====================================================================
        self.scheduler.add_job(
            func=self._execute_with_wrapper(
                ejecutar_proceso_dias_especificos,
                "Specific Days Process"
            ),
            trigger=CronTrigger(day_of_week='mon,wed,fri', hour=6, minute=30),
            id="proceso_dias_especificos",
            name="Specific Days Process (Mon, Wed, Fri 06:30 AM)",
            replace_existing=True
        )
        logger.info("✅ Configured: Specific Days Process (Mon, Wed, Fri 06:30 AM)")

        # ====================================================================
        # 4. CRON PROCESS - Every 4 hours on the hour
        # ====================================================================
        self.scheduler.add_job(
            func=self._execute_with_wrapper(ejecutar_proceso_cron, "Cron Process"),
            trigger=CronTrigger(hour='*/4', minute=0),
            id="proceso_cron",
            name="Cron Process (every 4 hours)",
            replace_existing=True
        )
        logger.info("✅ Configured: Cron Process (every 4 hours - expression: 0 */4 * * *)")

        # ====================================================================
        # 5. CONTINUOUS PROCESS - Permanent worker
        # ====================================================================
        # This runs in a separate loop, not with scheduler
        continuous_task = asyncio.create_task(
            self._continuous_process_loop()
        )
        self.continuous_tasks.append(continuous_task)
        logger.info("✅ Configured: Continuous Process (permanent worker)")

        # ====================================================================
        # 6. EVENT MONITOR - Listen to external events
        # ====================================================================
        monitor_task = asyncio.create_task(
            self._event_monitor_loop()
        )
        self.continuous_tasks.append(monitor_task)
        logger.info("✅ Configured: Event Monitor (triggered by files/flags/webhooks)")

        # Start scheduler
        self.scheduler.start()
        logger.info("🚀 Scheduler started")

        # Show scheduled jobs summary
        self._show_scheduled_jobs()

        logger.info("✅ Scheduler Service started successfully")

    async def stop_service(self):
        """
        Stop the service gracefully.
        """
        logger.info("🔴 Stopping Scheduler Service...")

        self.running = False

        # Stop scheduler
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("✅ Scheduler stopped")

        # Cancel continuous tasks
        for task in self.continuous_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("✅ Scheduler Service stopped")

    def _execute_with_wrapper(self, function, name: str):
        """
        Wrapper to execute async functions with error handling.

        Args:
            function: Async function to execute
            name: Process name
        """
        async def wrapper():
            try:
                logger.info(f"▶️ Executing: {name}")
                await function()
                logger.info(f"✅ {name} completed")
            except Exception as e:
                logger.error(f"❌ Error in {name}: {e}", exc_info=True)

        return wrapper

    async def _continuous_process_loop(self):
        """
        Loop for continuous process that runs constantly.
        """
        logger.info("♾️ Starting continuous process loop...")

        while self.running:
            try:
                await ejecutar_proceso_continuo_iteracion()
                # Pause between iterations
                await asyncio.sleep(10)  # Every 10 seconds
            except asyncio.CancelledError:
                logger.info("♾️ Continuous loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in continuous loop: {e}", exc_info=True)
                # Wait before retrying
                await asyncio.sleep(30)

    async def _event_monitor_loop(self):
        """
        Loop for monitoring external events.

        In production, this would use:
        - watchdog to monitor filesystem
        - Database polling for flags
        - Message queue subscription
        - HTTP server for webhooks
        """
        logger.info("👁️ Starting event monitor...")

        # Initialize monitor
        await monitorear_eventos()

        # Simulate continuous monitoring
        iteration = 0
        while self.running:
            try:
                iteration += 1

                # Simulate event checking
                # In production, this would be real monitoring
                await asyncio.sleep(15)  # Check every 15 seconds

                # Simulate event every 3rd iteration (for demo)
                if iteration % 3 == 0:
                    logger.info(f"🎯 [MONITOR] Event detected at iteration {iteration}")
                    await ejecutar_proceso_evento(
                        trigger_info=f"DB flag detected (iteration {iteration})"
                    )

            except asyncio.CancelledError:
                logger.info("👁️ Event monitor cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in event monitor: {e}", exc_info=True)
                await asyncio.sleep(30)

    def _show_scheduled_jobs(self):
        """
        Show summary of all scheduled jobs.
        """
        logger.info("="*70)
        logger.info("📋 SCHEDULED JOBS:")
        logger.info("="*70)

        jobs = self.scheduler.get_jobs()

        for job in jobs:
            logger.info(f"  📌 {job.name}")
            logger.info(f"     ID: {job.id}")
            logger.info(f"     Trigger: {job.trigger}")
            if hasattr(job.trigger, 'next_run_time'):
                next_run = job.trigger.next_run_time
                if next_run:
                    logger.info(f"     Next execution: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("")

        logger.info(f"  ♾️ Continuous Process: Running permanently")
        logger.info(f"  👁️ Event Monitor: Active")
        logger.info("="*70)

    async def execute_process_manually(self, process_name: str):
        """
        Execute a process manually (useful for testing or external triggers).

        Args:
            process_name: Name of the process to execute
        """
        logger.info(f"🎯 Manual execution requested: {process_name}")

        available_processes = {
            "intervalo": ejecutar_proceso_intervalo,
            "hora_fija": ejecutar_proceso_hora_fija,
            "dias_especificos": ejecutar_proceso_dias_especificos,
            "cron": ejecutar_proceso_cron,
            "evento": lambda: ejecutar_proceso_evento("Manual trigger"),
            "continuo": ejecutar_proceso_continuo_iteracion,
        }

        if process_name in available_processes:
            await available_processes[process_name]()
        else:
            logger.error(f"❌ Process '{process_name}' not found")
            logger.info(f"Available processes: {list(available_processes.keys())}")


# ============================================================================
# AUXILIARY FUNCTION FOR TESTING
# ============================================================================

async def test_all_processes():
    """
    Auxiliary function to test all processes once.
    Useful for testing without waiting for schedules.
    """
    logger.info("🧪 TEST MODE: Executing all processes once...")
    logger.info("="*70)

    processes = [
        ("Interval Process", ejecutar_proceso_intervalo),
        ("Fixed Time Process", ejecutar_proceso_hora_fija),
        ("Specific Days Process", ejecutar_proceso_dias_especificos),
        ("Cron Process", ejecutar_proceso_cron),
        ("Event Process", lambda: ejecutar_proceso_evento("Manual test")),
        ("Continuous Process", ejecutar_proceso_continuo_iteracion),
    ]

    for name, function in processes:
        logger.info(f"\n{'='*70}")
        logger.info(f"🧪 Testing: {name}")
        logger.info(f"{'='*70}")

        try:
            await function()
            logger.info(f"✅ {name} - OK")
        except Exception as e:
            logger.error(f"❌ {name} - ERROR: {e}")

        # Pause between tests
        await asyncio.sleep(1)

    logger.info("\n" + "="*70)
    logger.info("🧪 TEST COMPLETED")
    logger.info("="*70)
