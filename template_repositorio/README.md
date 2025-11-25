# Repository Template - Shared Library

Generic template for creating a shared library that centralizes data access, configuration, and common utilities.

## ⚠️ IMPORTANT: Centralized Configuration

**This is the ONLY place where environment variables are defined** for all templates (API, Web, Console).

```
repositorio_lib/config/
├── settings.py      # ← Definitions with Pydantic BaseSettings
├── env.py           # Data preloading (APP_ENV)
├── cache.py         # Cache configuration
├── .env.example     # Configuration template
└── .env             # ← Environment variables (create from .env.example)
```

**Architecture:**
- All templates import configuration from `repositorio_lib.config.settings`
- NO individual `.env` files in each template
- Global instances (`db_settings`, `jwt_settings`, `app_settings`, `email_settings`) are available to all

## Features

- ✅ Asynchronous PostgreSQL connection with connection pooling
- ✅ Dual logging system (simple `logger` + `structured_logger` with context)
- ✅ Daily log rotation with automatic folder creation
- ✅ Performance monitoring utilities (`log_performance`)
- ✅ Auto-generated SQLAlchemy models from database
- ✅ Auto-generated Pydantic schemas (base + complete with relationships)
- ✅ Generic CRUD helpers for async operations
- ✅ **Centralized configuration (SINGLE .env FOR ENTIRE ECOSYSTEM)**
- ✅ Retry utilities with exponential backoff
- ✅ Email notifications (SMTP)
- ✅ Date/time parsing utilities
- ✅ Chilean RUT validation and formatting
- ✅ Encryption and password hashing (bcrypt)

## Structure

```
repositorio_lib/
├── config/         # Configuration, settings, cache, logger exports
│   ├── settings.py     # Pydantic settings classes
│   ├── .env.example    # SINGLE configuration template for entire ecosystem
│   ├── cache.py        # Simple in-memory cache
│   └── logger.py       # Logger exports (logger, structured_logger)
│
├── core/           # Core infrastructure
│   ├── database.py     # Async PostgreSQL connection pool
│   ├── logger.py       # Logging system implementation
│   ├── security.py     # JWT and authentication
│   └── crypto.py       # Encryption and password hashing
│
├── utils/          # Data operations and shared utilities
│   ├── crud_helpers.py # Generic async CRUD operations
│   ├── retry.py        # Retry decorators with exponential backoff
│   ├── email_sender.py # SMTP email notifications
│   ├── date_utils.py   # Date/time parsing and validation
│   ├── rut_utils.py    # Chilean RUT utilities
│   └── util.py         # General utilities
│
├── model/          # SQLAlchemy models (auto-generated with sqlacodegen)
├── schema/         # Pydantic schemas (auto-generated with schema_generator.py)
└── service/        # Data access layer (repository pattern)
```

## Installation

### Main environment (development)

```bash
cd your_data_layer
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

### Model generation environment

```bash
py -3.12 -m venv env
env\Scripts\activate
pip install -r model_gen.txt
```

## Usage in Other Projects

### Step 1: Install as dependency

In project's `requirements.txt`:
```
-e ../repositorio_lib
```

Or directly:
```bash
pip install -e ../repositorio_lib
```

### Step 2: Configure environment variables

**⚠️ CRITICAL:** Create `.env` file in `repositorio_lib/config/`

```bash
cd repositorio_lib/config
cp .env.example .env
# Edit .env with all variables
```

### Step 3: Use in code

```python
# ⭐ Configuration (global instances)
from repositorio_lib.config.settings import db_settings, jwt_settings, app_settings, email_settings

# Core functionality
from repositorio_lib.core.database import get_async_session
from repositorio_lib.core import setup_logger, get_logger, log_performance

# Data access
from repositorio_lib.service.repository import v1Repository

# Utilities
from repositorio_lib.utils import (
    retry_with_backoff,
    get_all_async,
    send_email,
    validate_rut,
)

# Usage examples
connection_string = db_settings.get_connection_string(async_mode=True)
secret_key = jwt_settings.SECRET_KEY
log_directory = app_settings.get_log_dir()

# Logger setup (in application main.py)
logger = setup_logger("my_service", level=logging.INFO)
```

## Regenerate Models

```bash
env\Scripts\activate
sqlacodegen postgresql+psycopg2://user:pass@host:port/db > your_data_layer/model/models.py

# Clean null bytes (Windows)
(Get-Content your_data_layer/model/models.py -Raw) -replace [char]0, '' | Set-Content your_data_layer/model/models.py

# Generate schemas
python schema_generator.py
```

## License

Free code template for use in Python projects
