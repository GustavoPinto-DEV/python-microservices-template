"""
Batch Process Example

This module shows how to implement a typical batch process.
You can use this file as a base to create your own processes.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any

# Centralized logger
from config.logger import logger

# TODO: Uncomment when you have repositorio_lib
# from repositorio_lib.core.database import get_async_session
# from repositorio_lib.service.repository import v1Repositorio


async def execute_example_process():
    """
    Example process showing typical structure of a batch process.

    This process:
    1. Queries data from the database
    2. Processes the records
    3. Updates results in the database
    4. Records metrics
    """
    logger.info("📊 Starting example process...")

    try:
        # Process metrics
        start_time = datetime.now()
        processed = 0
        successful = 0
        failed = 0

        # Step 1: Get data to process
        logger.info("1️⃣ Getting data to process...")
        records = await get_pending_records()
        logger.info(f"   Found {len(records)} pending records")

        if not records:
            logger.info("   No pending records. Finishing.")
            return

        # Step 2: Process records
        logger.info("2️⃣ Processing records...")
        for record in records:
            try:
                await process_record(record)
                successful += 1
            except Exception as e:
                logger.error(f"   Error processing record {record.get('id')}: {e}")
                failed += 1
            finally:
                processed += 1

            # Progress log every 10 records
            if processed % 10 == 0:
                logger.info(f"   Progress: {processed}/{len(records)}")

        # Step 3: Record results
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("3️⃣ Process completed:")
        logger.info(f"   Total processed: {processed}")
        logger.info(f"   Successful: {successful}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Duration: {duration:.2f}s")

        # TODO: Save process metrics to DB if needed
        # await save_process_metrics(processed, successful, failed, duration)

    except Exception as e:
        logger.error(f"❌ Error in example process: {e}", exc_info=True)
        raise


async def get_pending_records() -> List[Dict[str, Any]]:
    """
    Get pending records to process from the database.

    Returns:
        List of pending records
    """
    # TODO: Implement real database query
    # async with get_async_session() as db:
    #     repositorio = v1Repositorio()
    #     result = await repositorio.get_registros_pendientes(db)
    #     return result.data

    # Example data
    await asyncio.sleep(0.5)  # Simulate DB query
    return [
        {"id": 1, "nombre": "Record 1", "valor": 100},
        {"id": 2, "nombre": "Record 2", "valor": 200},
        {"id": 3, "nombre": "Record 3", "valor": 300},
    ]


async def process_record(record: Dict[str, Any]):
    """
    Process an individual record.

    Args:
        record: Record data to process
    """
    logger.debug(f"   Processing record {record['id']}: {record['nombre']}")

    # TODO: Implement processing logic
    # Examples:
    # - Validate data
    # - Calculate values
    # - Call external APIs
    # - Update database

    # Simulate processing
    await asyncio.sleep(0.1)

    # Example: Update in DB
    # async with get_async_session() as db:
    #     await repositorio.actualizar_registro(
    #         db,
    #         record['id'],
    #         {"procesado": True, "fecha_proceso": datetime.now()}
    #     )
    #     await db.commit()

    logger.debug(f"   ✓ Record {record['id']} processed successfully")


# Examples of other common process types

async def api_integration_process():
    """
    Example of external API integration.
    """
    import httpx

    logger.info("🌐 Starting external API integration...")

    try:
        async with httpx.AsyncClient() as client:
            # Call external API
            response = await client.get("https://api.example.com/data")
            response.raise_for_status()
            data = response.json()

            # Process data
            logger.info(f"Received {len(data)} records from API")

            # Save to DB
            # async with get_async_session() as db:
            #     for item in data:
            #         await repositorio.crear_o_actualizar(db, item)
            #     await db.commit()

            logger.info("✅ API integration completed")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in external API: {e.response.status_code}")
        raise
    except Exception as e:
        logger.error(f"Error in API integration: {e}", exc_info=True)
        raise


async def data_cleanup_process():
    """
    Example of data cleanup/maintenance process.
    """
    logger.info("🧹 Starting data cleanup...")

    try:
        # Example: Delete old records
        retention_days = 90

        # async with get_async_session() as db:
        #     cutoff_date = datetime.now() - timedelta(days=retention_days)
        #
        #     # Delete old records
        #     result = await repositorio.eliminar_registros_antiguos(
        #         db,
        #         cutoff_date
        #     )
        #
        #     await db.commit()
        #     logger.info(f"Deleted {result.count} old records")

        # Example: Clean duplicates
        # await clean_duplicates(db)

        logger.info("✅ Cleanup completed")

    except Exception as e:
        logger.error(f"Error in data cleanup: {e}", exc_info=True)
        raise


async def report_generation_process():
    """
    Example of report generation.
    """
    logger.info("📋 Generating report...")

    try:
        # Collect data
        # async with get_async_session() as db:
        #     data = await repositorio.obtener_datos_reporte(db)

        # Generate report (CSV, PDF, Excel, etc.)
        # import pandas as pd
        # df = pd.DataFrame(data)
        # df.to_csv(f"report_{datetime.now().strftime('%Y%m%d')}.csv")

        # Send via email
        # await send_email_with_report(report_file)

        logger.info("✅ Report generated and sent")

    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        raise


async def parallel_batch_process():
    """
    Example of parallel batch processing.
    """
    logger.info("⚡ Starting parallel processing...")

    try:
        # Get records to process
        records = await get_pending_records()

        # Process in parallel batches
        batch_size = 10
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            # Process batch in parallel
            tasks = [process_record(rec) for rec in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successes and errors
            successful = sum(1 for r in results if not isinstance(r, Exception))
            errors = len(results) - successful

            logger.info(f"Batch {i//batch_size + 1}: {successful} ok, {errors} errors")

        logger.info("✅ Parallel processing completed")

    except Exception as e:
        logger.error(f"Error in parallel processing: {e}", exc_info=True)
        raise


# TODO: Add your own processes here
# Additional examples:
# - SFTP synchronization
# - Notification sending
# - Statistical calculations
# - Anomaly detection
# - Cache updates
