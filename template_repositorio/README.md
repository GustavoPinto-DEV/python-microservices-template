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

- ✅ Asynchronous PostgreSQL connection
- ✅ Optimized connection pool
- ✅ Centralized logger with rotation
- ✅ Auto-generated models from DB
- ✅ Auto-generated Pydantic schemas
- ✅ CRUD helpers
- ✅ **Centralized settings (SINGLE CONFIGURATION POINT)**
- ✅ Shared utilities

## Structure

```
your_data_layer/
├── config/         # Configuration (settings, cache)
├── core/           # Core functionality (db, logger, security)
├── utils/          # Shared utilities
├── model/          # SQLAlchemy models (auto-generated)
├── schema/         # Pydantic schemas (auto-generated)
└── service/        # Repository (data access layer)
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

# Database
from repositorio_lib.core.database import get_async_session
from repositorio_lib.core.logger import setup_logger
from repositorio_lib.service.repository import v1Repositorio
from repositorio_lib.utils import retry_with_backoff

# Usage example
connection_string = db_settings.get_connection_string(async_mode=True)
secret_key = jwt_settings.SECRET_KEY
log_directory = app_settings.get_log_dir()
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
