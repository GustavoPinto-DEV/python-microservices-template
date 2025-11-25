# Console Template - Asyncio Batch Service

Generic template for console/batch services based on asyncio for background processing.

## Features

- ✅ Asynchronous execution with asyncio
- ✅ Continuous or scheduled batch processing
- ✅ Graceful signal handling (SIGINT, SIGTERM)
- ✅ Dual logging system (simple `logger` + `structured_logger` with context)
- ✅ Asynchronous PostgreSQL connection
- ✅ Automatic retries with exponential backoff
- ✅ Integration with external services (APIs, SFTP)
- ✅ Docker ready

## Project Structure

```
template_consola/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container
├── PROCESOS_PARALELOS.md      # ⭐ Parallel execution guide
├── config/
│   └── env.py                 # Global environment variables
├── dependencies/
│   └── util.py                # Project utilities
├── exception/
│   └── exception_handlers.py # Error handlers
├── processes/
│   ├── ejemplo_proceso.py     # Example batch process
│   ├── proceso_a.py          # 🔵 Process A (data update)
│   ├── proceso_b.py          # 🟢 Process B (report generation)
│   └── proceso_c.py          # 🟡 Process C (cleanup/maintenance)
├── service/
│   └── servicio.py           # Service orchestration
└── schema/
    └── schemas.py            # Pydantic schemas
```

**⚠️ NOTE:** This template does NOT have its own `.env.example` file. All environment variables are centrally managed in `../template_repositorio/repositorio_lib/config/.env.example`

## Use Cases

This template is ideal for:

- **Batch processing**: Massive data updates, periodic calculations
- **Synchronization**: Integration with external systems (APIs, SFTP, FTP)
- **Monitoring**: Anomaly detection, automatic alerts
- **Data cleanup**: Purging old records, database maintenance
- **Report generation**: Scheduled reports, email sending
- **Workers**: Task queue processing

## Parallel Process Execution

The template includes **3 example processes** that run in parallel using `asyncio.gather()`:

```
┌─────────────────────────────────────────┐
│         Main Service                    │
│         (service/servicio.py)           │
└────────────────┬────────────────────────┘
                 │
                 │ asyncio.gather()
                 │
        ┌────────┼────────┐
        │        │        │
    ┌───▼───┐ ┌─▼───┐ ┌──▼──┐
    │Proc A │ │Proc B│ │Proc C│  ⚡ In parallel
    │ 🔵   │ │ 🟢  │ │ 🟡  │
    │ 5.5s │ │ 6s  │ │ 6s  │
    └───────┘ └─────┘ └─────┘
```

**Total time: ~6 seconds** (vs 17.5s if sequential)

### Execution Options

1. **Sequential**: One process after another
2. **Parallel**: All simultaneously (⭐ active by default)
3. **Combined**: Critical process first, then others in parallel

See complete details in **`PROCESOS_PARALELOS.md`**

## Installation

### 1. Create virtual environment

```bash
py -3.12 -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

**⚠️ IMPORTANT:** Environment variables are NOT configured in this template.

All variables are centrally managed in `repositorio_lib/config/.env`

```bash
# Configure variables in the shared repository
cd ../repositorio_lib/config
cp .env.example .env
# Edit .env with DB, logging, etc.
```

This template will automatically import configuration from `repositorio_lib.config.settings`

### 4. Execute

```bash
python main.py
```

## Configuration

**⚠️ CONFIGURE IN:** `repositorio_lib/config/.env`

### Execution Interval

```bash
MINUTOS_CONSOLA=60  # Execute every 60 minutes
```

### Execution Mode

```bash
# Continuous execution (infinite loop)
ENABLE_CONTINUOUS_MODE=true

# Single execution (terminates after 1 cycle)
ENABLE_CONTINUOUS_MODE=false
```

**Note:** These variables are read from `service/servicio.py` which imports from `repositorio_lib.config.settings` or uses `os.getenv()` directly.

## Adding a New Process

### 1. Create file in `processes/`

```python
# processes/my_process.py

from config.logger import logger, structured_logger
from datetime import datetime

async def execute_my_process():
    """
    Executes batch process logic with structured logging.
    """
    start_time = datetime.now()
    job_id = f"my_process_{start_time.strftime('%Y%m%d_%H%M%S')}"

    # Set context for all logs in this process
    structured_logger.set_context(
        job_id=job_id,
        execution_date=start_time.isoformat(),
        process_name="my_process"
    )

    logger.info("Starting my process...")

    try:
        # Your logic here
        # - Query database
        # - Process records
        # - Call external APIs

        # Log progress with metrics
        structured_logger.info(
            "Batch process completed",
            records_total=100,
            processed=100,
            successful=95,
            failed=5,
            duration_seconds=round((datetime.now() - start_time).total_seconds(), 2),
            status="completed",
            event_type="batch_completed"
        )

        logger.info("Process completed successfully")
    finally:
        structured_logger.clear_context()
```

### 2. Register in `service/servicio.py`

```python
from processes.my_process import execute_my_process

async def execute_cycle(self):
    # Add your process to the cycle
    await execute_my_process()
```

## Error Handling

The service includes automatic retries:

```python
from your_data_layer.utils import retry_with_backoff

await retry_with_backoff(
    my_function,
    name="My Process",
    max_attempts=3,
    initial_delay=5
)
```

## Stopping the Service

### Interactive mode

```bash
Ctrl+C
```

### Docker

```bash
docker stop <container-id>
```

The service always performs a graceful shutdown, completing the current task before stopping.

## Docker

### Build

```bash
docker build -t consola-template .
```

### Run

```bash
# Environment variables from repositorio_lib
docker run \
  -v $(pwd)/../repositorio_lib:/app/repositorio_lib \
  --env-file ../repositorio_lib/config/.env \
  consola-template
```

### With Docker Compose

```yaml
services:
  consola:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    env_file:
      - ../repositorio_lib/config/.env  # ← Centralized configuration
    volumes:
      - ../repositorio_lib:/app/repositorio_lib
      - ${LOG_HOST_PATH}:${LOG_DIR_EXTERNAL}
```

## Integration with Shared Repository

This template **requires** a shared library (`repositorio_lib`) to function.

### Install shared library

```bash
# Assuming you have the repository in the parent directory
pip install -e ../repositorio_lib
```

### Centralized configuration

**ALL environment variables are managed in:**

```
../repositorio_lib/config/
├── settings.py      # Configuration with Pydantic
├── .env             # Environment variables (create from .env.example)
└── .env.example     # Configuration template
```

### Use in code

```python
# Configuration
from repositorio_lib.config.settings import db_settings, app_settings, console_settings

# Core infrastructure
from repositorio_lib.core.database import get_async_session
from repositorio_lib.core import setup_logger, log_performance

# Data access
from repositorio_lib.service.repository import v1Repository

# Utilities
from repositorio_lib.utils import retry_with_backoff, get_all_async, send_email

# Logging (in your template)
from config.logger import logger, structured_logger

# Usage examples
db_url = db_settings.get_connection_string(async_mode=True)
log_dir = app_settings.get_log_dir()
batch_size = console_settings.BATCH_SIZE
max_retries = console_settings.MAX_RETRIES
```

## Logging

This template includes a dual logging system optimized for batch processing:

### Simple Logger (`logger`)

Use for application lifecycle, debug traces, and infrastructure operations:

```python
from config.logger import logger

logger.info("Starting batch service...")
logger.debug("Connecting to database")
logger.error("Connection failed", exc_info=True)
```

### Structured Logger (`structured_logger`)

Use for batch metrics, job tracking, and business events:

```python
from config.logger import structured_logger

# Set context for entire batch job
structured_logger.set_context(
    job_id="batch_20250125_120000",
    execution_date="2025-01-25T12:00:00",
    process_name="data_sync"
)

# Log progress with metrics
structured_logger.info(
    "Processing progress",
    processed=500,
    total=1000,
    successful=490,
    failed=10,
    progress_percentage=50.0,
    event_type="batch_progress"
)

# Log final results
structured_logger.info(
    "Batch completed",
    records_total=1000,
    processed=1000,
    successful=980,
    failed=20,
    duration_seconds=145.32,
    success_rate=98.0,
    status="completed",
    event_type="batch_completed"
)

# Always clear context when done
structured_logger.clear_context()
```

### When to Use Each

- **Use `logger`**: Service startup/shutdown, signal handling, retry attempts, cache operations
- **Use `structured_logger`**: Batch cycles, job metrics, record processing, business events

### Log Files

- Development: `./logs/YYYY-MM-DD/template_consola.log`
- Production: `/var/log/app/logs/YYYY-MM-DD/template_consola.log`
- Daily rotation with automatic folder creation at midnight
- Thread-safe for async operations

## Process Examples

### Update data from external API

```python
async def update_external_data():
    async with get_async_session() as db:
        # Get data from API
        data = await call_external_api()

        # Update in database
        for item in data:
            await repository.update_record(db, item)

        await db.commit()
```

### Batch processing with SFTP

```python
async def process_sftp_files():
    # Connect to SFTP
    async with connect_sftp() as sftp:
        # Download files
        files = await sftp.list_files()

        for file in files:
            # Process file
            content = await sftp.download(file)
            await process_content(content)

            # Move to processed folder
            await sftp.move(file, "/processed/")
```

## Monitoring

### Logs

Logs are saved in:
- Development: `./logs/`
- Production: `/var/log/app/logs/`

### Health Check

To verify that the service is running:

```bash
# View logs in Docker
docker logs <container-id>

# View processes
ps aux | grep python
```

## License

Free code template for use in Python projects
