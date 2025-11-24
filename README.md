# Python Microservices Templates

Complete set of production-ready templates designed to kickstart Python projects with standardized architecture and enterprise best practices.

## 📦 Available Templates

### 1. **template_api** - REST API with FastAPI
Complete template for creating REST APIs with JWT authentication, response compression, and rate limiting.

**Features:**
- ✅ FastAPI with automatic documentation (Swagger/ReDoc)
- ✅ JWT authentication
- ✅ Compression middleware (gzip)
- ✅ Optional IP-based rate limiting
- ✅ Centralized exception handling
- ✅ Structured logging
- ✅ Asynchronous PostgreSQL connection (optional)
- ✅ Router → Controller → Repository architecture

**Usage:**
```bash
cp -r template_api my_new_api
cd my_new_api
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --port 8000 --reload
```

---

### 2. **template_consola** - Batch/Background Service
Template for console services that run batch processes in the background.

**Features:**
- ✅ Asynchronous execution with asyncio
- ✅ Continuous or scheduled batch processing
- ✅ Graceful signal handling (SIGINT, SIGTERM)
- ✅ Automatic retries with exponential backoff
- ✅ Integration with external services (APIs, SFTP)
- ✅ Daily log rotation

**Use cases:**
- Bulk data updates
- External system synchronization
- Scheduled report generation
- Data cleanup and maintenance
- Queue processing

**Usage:**
```bash
cp -r template_consola my_batch_service
cd my_batch_service
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

---

### 3. **template_web** - Web Application with Jinja2
Template for web applications with FastAPI and server-side rendering using Jinja2.

**Features:**
- ✅ FastAPI + Jinja2 templates
- ✅ Cookie-based authentication
- ✅ Reusable base templates (layout, datatable, log, detail)
- ✅ Jinja2 macros for common components
- ✅ DataTables with server-side processing
- ✅ Global loader system
- ✅ Static files (CSS, JS, images)
- ✅ HTML forms with validation
- ✅ User sessions
- ✅ MVC architecture

**Usage:**
```bash
cp -r template_web my_web_app
cd my_web_app
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --port 8000 --reload
```

---

### 4. **template_repositorio** - Shared Library
Template for creating an internal reusable library that centralizes data access, configuration, and utilities.

**Features:**
- ✅ Asynchronous PostgreSQL connection with optimized pool
- ✅ Centralized logger with daily rotation
- ✅ Centralized settings with Pydantic
- ✅ Auto-generable SQLAlchemy models
- ✅ Auto-generable Pydantic schemas
- ✅ CRUD helpers
- ✅ Shared utilities
- ✅ TTL-based cache system

**Usage:**
```bash
cp -r template_repositorio my_data_layer
cd my_data_layer

# Main environment
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# Environment for model generation
py -3.12 -m venv env
env\Scripts\activate
pip install -r model_gen.txt
```

**Generate models from DB:**
```bash
env\Scripts\activate
sqlacodegen postgresql+psycopg2://user:pass@host:port/db > your_lib/model/models.py
```

---

## 🏗️ Typical Project Architecture

```
my_project/
├── api/              # REST API (template_api)
├── web/              # Web application (template_web)
├── worker_1/         # Batch service 1 (template_consola)
├── worker_2/         # Batch service 2 (template_consola)
├── data_layer/       # Shared library (template_repositorio)
│   └── repositorio_lib/
│       └── config/
│           └── .env  # ← CENTRALIZED environment variables (single location)
└── docker-compose.yml
```

**IMPORTANT:** Environment variables are managed exclusively in `data_layer/repositorio_lib/config/.env`

### Data Flow

```
┌─────────────────────────────────────────────────┐
│         PostgreSQL Database                     │
└──────────────────┬──────────────────────────────┘
                   │
                   │ SQLAlchemy Async + AsyncPG
                   │
     ┌─────────────▼─────────────┐
     │  data_layer (library)     │
     │  - Models                 │
     │  - Schemas                │
     │  - Repository             │
     │  - Config                 │
     │  - Logger                 │
     │  - Utilities              │
     └────────┬──────────────────┘
              │
   ┌──────────┼──────────┬────────┐
   │          │          │        │
┌──▼──┐  ┌───▼───┐  ┌───▼───┐  ┌─▼─────┐
│ API │  │  Web  │  │Worker │  │Worker │
│     │  │       │  │   1   │  │   2   │
└─────┘  └───────┘  └───────┘  └───────┘
```

---

## 🚀 Quick Start Guide

### Step 1: Create Data Layer (Shared Library)

```bash
cp -r template_repositorio my_project/data_layer
cd my_project/data_layer
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Step 2: Configure Environment Variables (CENTRALIZED)

**⚠️ IMPORTANT:** This is the ONLY place where environment variables are defined.

```bash
cd repositorio_lib/config
cp .env.example .env
# Edit .env with your values (DB, JWT, SMTP, etc.)
```

All services (API, Web, Workers) will automatically use this configuration.

### Step 3: Create Your First API

```bash
cd my_project
cp -r templates/template_api api
cd api
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e ../data_layer  # Install shared library (includes config)
# NO .env needed here - use data_layer/repositorio_lib/config/.env
uvicorn main:app --port 8000 --reload
```

### Step 4: Add More Services

Repeat the process with `template_web`, `template_consola`, etc. All will use the same centralized configuration.

---

## 📋 Template Customization

### Modifying Names

When copying a template, update:

1. **Configuration names** (titles, descriptions)
2. **Module names** in imports if necessary
3. **Log file names**
4. **Environment variables**

### Adding Functionality

Each template has sections marked with `TODO:` indicating where to add your specific logic.

**Example - Adding API endpoint:**

1. **Router** (`router/v1Router.py`):
```python
@router.get("/my-endpoint")
async def my_endpoint(controller: v1Controller = Depends(get_controller)):
    return await controller.my_method()
```

2. **Controller** (`controller/v1Controller.py`):
```python
async def my_method(self):
    result = await self.repository.my_query()
    return result
```

3. **Repository** (`data_layer/service/repository.py`):
```python
async def my_query(self):
    # Data access logic
    pass
```

---

## 🐳 Docker

Each template includes a ready-to-use `Dockerfile`.

**Complete docker-compose.yml example:**

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: api/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - data_layer/repositorio_lib/config/.env  # ← Centralized configuration
    volumes:
      - logs:/var/log/app/logs
      - ./data_layer:/app/data_layer

  web:
    build:
      context: .
      dockerfile: web/Dockerfile
    ports:
      - "8001:8000"
    env_file:
      - data_layer/repositorio_lib/config/.env  # ← Centralized configuration
    volumes:
      - ./data_layer:/app/data_layer

  worker_1:
    build:
      context: .
      dockerfile: worker_1/Dockerfile
    env_file:
      - data_layer/repositorio_lib/config/.env  # ← Centralized configuration
    volumes:
      - ./data_layer:/app/data_layer

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  logs:
  postgres_data:
```

**Note:** All variables are loaded from `data_layer/repositorio_lib/config/.env`

For production deployment with Docker, see the [Deployment Documentation](docs/deployment/).

---

## 🔧 Environment Variable Configuration

**⚠️ IMPORTANT:** Environment variables are centrally managed in:

```
template_repositorio/repositorio_lib/config/.env
```

**DO NOT create .env files in individual templates.**

### Configuration

```bash
cd template_repositorio/repositorio_lib/config
cp .env.example .env
```

Edit `.env` with your values:

```bash
# Environment
ENVIRONMENT=dev

# Database
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db

# JWT (for API & Web)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Logging
LOG_DIR_DEV=logs
LOG_DIR_PRD=/var/log/app/logs

# Email (SMTP)
SMTP_HOST=smtp.example.com
SMTP_USER=user
SMTP_PASSWORD=password
EMAIL_OPERACIONES=ops@example.com

# Database Pool
POOL_SIZE=10
MAX_OVERFLOW=20
```

### Usage in Code

```python
from repositorio_lib.config.settings import db_settings, jwt_settings, app_settings

# Access configuration
db_url = db_settings.get_connection_string(async_mode=True)
secret = jwt_settings.SECRET_KEY
log_dir = app_settings.get_log_dir()
```

---

## 📝 Conventions and Best Practices

### Directory Structure

All templates follow the same structure:

```
project/
├── main.py              # ONLY .py in root
├── Dockerfile
├── requirements.txt
├── .env.example
├── config/              # Configuration
├── controller/          # Business logic (API/Web)
├── dependencies/        # Project-specific utilities
├── exception/           # Error handlers
├── router/              # Routes (API/Web)
├── processes/           # Batch processes (Console)
├── service/             # Services (Console)
└── schema/              # Pydantic schemas
```

### Import Pattern

```python
# Shared library (if applicable)
from your_data_layer.core.database import get_async_session
from your_data_layer.core.logger import setup_logger
from your_data_layer.service.repository import v1Repository
from your_data_layer.utils import retry_with_backoff

# Project-specific
from dependencies.util import my_utility
from dependencies.auth import get_current_user
```

---

## 🛠️ Troubleshooting

### Error: "No module named 'your_lib'"

```bash
# Install shared library in editable mode
pip install -e ../data_layer

# Add to .vscode/settings.json
{
  "python.analysis.extraPaths": ["../data_layer"]
}
```

### Error: "source code string cannot contain null bytes"

When generating models on Windows:

```powershell
(Get-Content your_lib/model/models.py -Raw) -replace [char]0, '' | Set-Content your_lib/model/models.py
```

---

## 📚 Resources

- **Individual README.md** in each template with specific documentation
- **Code comments** - All files are documented
- **Marked TODOs** - Key points to customize
- **[Deployment Documentation](docs/deployment/)** - Production deployment guides
- **[CLAUDE.md](CLAUDE.md)** - AI assistant guidance for this project

---

## 🚀 Production Deployment

For production deployment, we provide comprehensive guides for multiple deployment strategies:

- **[Docker Deployment](docs/deployment/guides/DOCKER_DEPLOYMENT.md)** - Complete Docker production setup
- **[Compiled Artifacts](docs/deployment/guides/COMPILED_ARTIFACTS.md)** - Windows Services, Linux Systemd, Wheels
- **[Quick Reference](docs/deployment/)** - Deployment documentation index

See the [deployment documentation](docs/deployment/) for detailed guides, configuration examples, and best practices.

---

## 🤝 Contributing

To improve the templates:

1. Identify improvements or bugs
2. Apply changes in your project
3. If beneficial for everyone, update the templates
4. Document the changes

---

## 📄 License

Free code templates for use in Python projects.

---

**Version:** 2.0.0
**Last Updated:** 2025-01-24
**Required Python:** 3.12+

