# Console Template - Asyncio Batch Service

Generic template for console/batch services based on asyncio for background processing.

## Features

- ✅ Asynchronous execution with asyncio
- ✅ Continuous or scheduled batch processing
- ✅ Graceful signal handling (SIGINT, SIGTERM)
- ✅ Structured logging with rotation
- ✅ Asynchronous PostgreSQL connection
- ✅ Automatic retries with exponential backoff
- ✅ Integration with external services (APIs, SFTP)
- ✅ Docker ready

## Project Structure

```
template_consola/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables (copy to .env)
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

import logging

logger = logging.getLogger(__name__)

async def execute_my_process():
    """
    Executes batch process logic.
    """
    logger.info("Starting my process...")

    # Your logic here
    # - Query database
    # - Process records
    # - Call external APIs
    # - Etc.

    logger.info("Process completed successfully")
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
from repositorio_lib.config.settings import db_settings, app_settings

# Database and utilities
from repositorio_lib.core.database import get_async_session
from repositorio_lib.core.logger import setup_logger
from repositorio_lib.service.repository import v1Repositorio
from repositorio_lib.utils import retry_with_backoff

# Usage example
db_url = db_settings.get_connection_string(async_mode=True)
log_dir = app_settings.get_log_dir()
```

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
