# Python Project Templates

A comprehensive collection of production-ready, modular templates for building scalable Python applications. This repository provides standardized architectures and best practices for APIs, console services, web applications, and shared internal libraries — all built on modern technologies such as FastAPI, asyncio, Jinja2, SQLAlchemy, and Docker.

## Overview

**Python Project Templates** accelerates new project creation while maintaining consistency, scalability, and clean architecture principles across your organization. Each template is independently usable yet designed to integrate seamlessly with others through a shared data layer.

## Available Templates

### 1. **template_api** - REST API with FastAPI

A complete template for building REST APIs with JWT authentication, automatic documentation, gzip compression, rate limiting, and centralized error handling.

**Key Features:**
- ✅ FastAPI with automatic API documentation (Swagger/ReDoc)
- ✅ JWT authentication and token management
- ✅ Gzip response compression middleware
- ✅ Rate limiting middleware (optional, IP-based)
- ✅ Centralized exception handling with consistent response format
- ✅ Structured logging with daily rotation
- ✅ Async PostgreSQL connectivity (SQLAlchemy + asyncpg)
- ✅ Clean architecture: Router → Controller → Repository → Database
- ✅ Health check and monitoring endpoints
- ✅ CORS middleware with configurable origins
- ✅ Docker-ready with Dockerfile included

**Quick Start:**
```bash
cp -r template_api my_api
cd my_api
python -3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
pre-commit install
uvicorn main:app --reload --port 8000
```

---

### 2. **template_consola** - Background/Batch Service

A template for building async background services that execute batch processes, scheduled jobs, or long-running tasks with graceful shutdown, retry logic, and external service integration.

**Key Features:**
- ✅ Async processing with asyncio event loop
- ✅ Continuous or interval-based batch execution
- ✅ Graceful signal handling (SIGINT, SIGTERM)
- ✅ Automatic retry logic with exponential backoff
- ✅ External service integration (APIs, SFTP, databases)
- ✅ Centralized logging with daily log rotation
- ✅ Configurable execution intervals
- ✅ Metrics and execution tracking
- ✅ Docker-ready with Dockerfile included

**Use Cases:**
- Bulk data updates and synchronization
- Integration with external systems
- Scheduled report generation
- Data cleanup and maintenance tasks
- Message queue processing
- Periodic health checks

**Quick Start:**
```bash
cp -r template_consola my_batch_service
cd my_batch_service
python -3.12 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python main.py
```

---

### 3. **template_web** - Server-Side Web Application

A template for building full-stack web applications combining FastAPI backend with Jinja2 server-side template rendering, cookie-based authentication, and rich HTML components.

**Key Features:**
- ✅ FastAPI + Jinja2 for server-side rendering
- ✅ Cookie-based session authentication
- ✅ Reusable Jinja2 template base and macros
- ✅ Bootstrap 5 integration for responsive UI
- ✅ DataTables with server-side processing
- ✅ Global page loader component
- ✅ MVC-style architecture
- ✅ Static asset management (CSS, JS, images)
- ✅ Form validation and error handling
- ✅ User session management
- ✅ Docker-ready with Dockerfile included

**Quick Start:**
```bash
cp -r template_web my_web_app
cd my_web_app
python -3.12 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

---

### 4. **template_repositorio** - Shared Data Layer Library

A reusable library that centralizes database access, configuration management, utilities, and common functionality shared across API, Web, and Batch services.

**Key Features:**
- ✅ Async PostgreSQL connectivity with connection pooling
- ✅ Centralized logger with daily rotation and multiple outputs
- ✅ Pydantic-based configuration management
- ✅ SQLAlchemy ORM models (auto-generatable from existing database)
- ✅ Repository pattern with CRUD helpers
- ✅ Reusable utility functions (retry, backoff, encryption)
- ✅ Shared Pydantic schemas for API responses
- ✅ Cache layer with TTL support
- ✅ Security helpers (password hashing, token generation)
- ✅ Installable as editable pip package

**Installation in Other Templates:**
```bash
# From within template_api, template_consola, or template_web
pip install -e ../template_repositorio
```

---

## Typical Project Structure

```
my_project/
├── api/                    # REST API (template_api)
├── web/                    # Web Application (template_web)
├── batch_worker_1/         # Background Service (template_consola)
├── batch_worker_2/         # Another Background Service (template_consola)
├── shared_lib/             # Shared Data Layer (template_repositorio)
├── .env                    # Shared environment variables
├── docker-compose.yml      # Orchestration configuration
└── README.md               # Project documentation
```

### Data Flow Diagram

```
┌─────────────────────────────────┐
│   PostgreSQL Database           │
└────────────────┬────────────────┘
                 │
        AsyncPG + SQLAlchemy
                 │
     ┌───────────▼──────────────┐
     │  Shared Data Layer       │
     │  (template_repositorio)  │
     │                          │
     │  - Models                │
     │  - Schemas               │
     │  - Repository Pattern    │
     │  - Configuration         │
     │  - Logger                │
     │  - Security Utilities    │
     └────┬────────────────┬────┘
          │                │
    ┌─────▼────┐      ┌────▼──────┐
    │   API    │      │    Web    │
    │          │      │           │
    │ FastAPI │      │ FastAPI +  │
    │  REST   │      │  Jinja2    │
    └─────┬────┘      └────┬──────┘
          │                │
    ┌─────▼──────────┬─────▼─────────┐
    │    Worker 1    │    Worker 2    │
    │  (Batch Jobs)  │  (Batch Jobs)  │
    │    asyncio     │    asyncio     │
    └────────────────┴────────────────┘
```

---

## Quick Start Guide

### Step 1: Create the Shared Data Layer

```bash
mkdir my_project && cd my_project
cp -r ../template_repositorio shared_lib
cd shared_lib

python -3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

cd ..
```

### Step 2: Create Your First API

```bash
cp -r ../template_api api
cd api

python -3.12 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install -e ../shared_lib
cp .env.example .env

# Configure .env with your database credentials and secrets
# Then start the API
uvicorn main:app --reload --port 8000
```

### Step 3: Add More Services

Repeat the process with `template_web`, `template_consola`, or additional instances of any template. Each service can be run in its own virtual environment and integrated via the shared data layer.

---

## Template Customization

### Modifying Configuration

Each template includes a `.env.example` file. Copy it to `.env` and customize:

```bash
# Environment
ENVIRONMENT=dev                    # dev, qa, prd

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database

# JWT (for APIs)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Logging
LOG_DIR_DEV=logs
LOG_DIR_EXTERNAL=/var/log/app/logs
LOG_LEVEL=INFO

# External Services
EXTERNAL_API_URL=https://api.example.com
EXTERNAL_API_KEY=your-api-key
EXTERNAL_API_TIMEOUT=30
```

### Adding New Endpoints (API)

1. **Define Schema** (`schema/schemas.py`):
   ```python
   from pydantic import BaseModel

   class MyRequest(BaseModel):
       name: str
       description: str
   ```

2. **Add Controller Logic** (`controller/v1Controller.py`):
   ```python
   async def my_method(self, request: MyRequest):
       # Implement business logic
       return MyResponse(...)
   ```

3. **Add Route** (`router/v1Router.py`):
   ```python
   @router.post("/my-endpoint")
   async def my_endpoint(request: MyRequest, controller = Depends(get_controller)):
       return await controller.my_method(request)
   ```

4. **Write Tests** (`tests/test_routers.py`):
   ```python
   def test_my_endpoint(client):
       response = client.post("/api/v1/my-endpoint", json={"name": "test"})
       assert response.status_code == 200
   ```

---

## Docker Deployment

### Single Service Docker Build

```bash
cd template_api
docker build -t my-api:latest .
docker run -p 8000:8000 --env-file .env my-api:latest
```

### Multi-Service Docker Compose

Create `docker-compose.yml` in your project root:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build:
      context: .
      dockerfile: api/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      - ./api:/app

  web:
    build:
      context: .
      dockerfile: web/Dockerfile
    ports:
      - "8001:8000"
    env_file:
      - .env
    depends_on:
      - db

  worker:
    build:
      context: .
      dockerfile: batch_worker_1/Dockerfile
    env_file:
      - .env
    depends_on:
      - db

volumes:
  postgres_data:
```

Start all services:
```bash
docker-compose up -d
```

---

## Code Quality and Testing

### Pre-commit Hooks

Install and configure pre-commit hooks automatically:

```bash
cd your_template_dir
pip install -r requirements-dev.txt
pre-commit install
```

Pre-commit will automatically run on every commit:
- **black**: Code formatting
- **isort**: Import sorting
- **ruff**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning

### Running Tests

```bash
# Run all tests with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run matching test pattern
pytest -k "auth" -v

# Run with coverage report
pytest tests/ --cov-report=term-missing
```

### Code Formatting

```bash
# Format code automatically
black .
isort .
ruff check --fix .

# Or use the Makefile (if available)
make format
```

---

## Database Management (API Templates)

### Using Alembic for Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Add user email field"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Auto-generating Models from Existing Database

```bash
cd template_repositorio

# Install model generation dependencies
pip install -r model_gen.txt

# Generate models from existing database
sqlacodegen postgresql://user:password@localhost:5432/database_name > \
  repositorio_lib/model/models.py
```

---

## Production Deployment Checklist

- [ ] Change `ENVIRONMENT=prd` in `.env`
- [ ] Update `SECRET_KEY` with a strong random value
- [ ] Configure specific CORS origins (not `["*"]`)
- [ ] Set up real database with production credentials
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure logging to external service or file system
- [ ] Set up monitoring and alerting
- [ ] Run security scan: `bandit -r .`
- [ ] Review dependencies: `safety check`
- [ ] Set appropriate API rate limits
- [ ] Test graceful shutdown and recovery
- [ ] Document any customizations made to templates
- [ ] Set up CI/CD pipeline (examples in `.github/workflows/`)

---

## Common Issues and Solutions

### "No module named 'shared_lib'"

Ensure the shared library is installed in editable mode:

```bash
pip install -e ../template_repositorio
```

Add to your IDE settings if needed (`.vscode/settings.json`):

```json
{
  "python.analysis.extraPaths": ["../template_repositorio"]
}
```

### Database Connection Errors

1. Verify PostgreSQL is running
2. Check `.env` database credentials
3. Verify network connectivity to database host
4. Test connection manually:
   ```bash
   python -c "from repositorio_lib.core.database import get_async_session; print('OK')"
   ```

### Import Errors After Modifying Shared Library

Clear Python cache and reinstall:

```bash
rm -rf __pycache__ .pytest_cache .mypy_cache
pip install -e ../template_repositorio --force-reinstall --no-deps
```

### Tests Failing with Coverage Below 80%

```bash
# View detailed coverage report
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html

# Identify uncovered code and add tests
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Python** | Python | 3.12+ |
| **Web Framework** | FastAPI | 0.115+ |
| **Server** | Uvicorn | 0.34+ |
| **Database** | PostgreSQL | 15+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Data Validation** | Pydantic | 2.0+ |
| **Authentication** | python-jose + bcrypt | JWT tokens |
| **Templates** | Jinja2 | 3.1+ |
| **Testing** | pytest | 7.4+ |
| **Code Quality** | black, ruff, mypy | Latest |
| **Containerization** | Docker | 20+ |
| **Async** | asyncio | Built-in |

---

## Contributing

To improve these templates:

1. Test changes thoroughly in your own project
2. Update affected templates if improvements are beneficial to all users
3. Document changes in template README files
4. Follow the existing code style and conventions
5. Ensure all tests pass before committing

---

## Best Practices

### Code Organization
- Keep business logic in controllers/services
- Separate database access in repository layer
- Use dependency injection (FastAPI `Depends`)
- Organize imports by type (stdlib, third-party, local)

### Async Programming
- Always use `async/await` for I/O operations
- Avoid blocking calls in async functions
- Use connection pools for database access
- Properly handle timeouts and cancellation

### Configuration
- Never hardcode secrets in code
- Use `.env` files for local development
- Use environment variables in production
- Validate configuration on startup

### Error Handling
- Use centralized exception handlers
- Return consistent error response formats
- Log errors with full context
- Expose only necessary details to clients

### Logging
- Use structured logging for better analysis
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include relevant context in log messages
- Avoid logging sensitive information

---

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLAlchemy Documentation**: https://sqlalchemy.org
- **Pydantic Documentation**: https://docs.pydantic.dev
- **Docker Documentation**: https://docs.docker.com
- **PostgreSQL Documentation**: https://www.postgresql.org/docs

---

## Version Information

| Item | Value |
|------|-------|
| **Template Version** | 2.1.0 |
| **Python Minimum** | 3.12 |
| **Last Updated** | 2025-01-15 |
| **Status** | Production Ready |

---

## License

These templates are provided as-is for use in Python projects. Feel free to modify and distribute according to your needs.

---

**Questions or Issues?** Refer to individual template README files for specific documentation, or review the code comments marked with `TODO:` to understand customization points.
