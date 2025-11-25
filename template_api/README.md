# API Template - FastAPI

Generic template for creating REST APIs with FastAPI, designed for enterprise projects with standardized architecture.

## Features

- ✅ FastAPI with automatic documentation (Swagger/ReDoc)
- ✅ JWT authentication
- ✅ Response compression middleware (gzip)
- ✅ Optional rate limiting
- ✅ Centralized exception handling
- ✅ Dual logging system (simple `logger` + `structured_logger` with context)
- ✅ Asynchronous PostgreSQL connection (optional)
- ✅ Clean architecture (Router → Controller → Repository)
- ✅ Docker ready
- ✅ Health check endpoints

## Project Structure

```
template_api/
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker container
├── config/
│   └── env.py          # Global environment variables
├── controller/
│   └── v1Controller.py # Business logic
├── dependencies/
│   ├── auth.py         # JWT authentication
│   └── util.py         # Project utilities
├── exception/
│   └── exception_handlers.py  # Error handlers
├── middleware/
│   ├── CompressionMiddleware.py   # Gzip response compression
│   └── RateLimiterMiddleware.py   # Rate limiting
├── router/
│   └── v1Router.py     # Route definitions
└── schema/
    └── schemas.py      # Pydantic schemas
```

**⚠️ NOTE:** This template does NOT have its own `.env.example` file. All environment variables are centrally managed in `../template_repositorio/repositorio_lib/config/.env.example`

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
# Edit .env with DB, JWT, SMTP, etc.
```

This template will automatically import configuration from `repositorio_lib.config.settings`

### 4. Run in development mode

```bash
uvicorn main:app --port 8000 --reload
```

## Usage

### Interactive Documentation

Once the server is started, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check

```bash
curl http://localhost:8000/health
```

## Adding a New Endpoint

### 1. Define route in `router/v1Router.py`

```python
@router.post("/users", response_model=UserResponse)
async def create_user(
    request: UserRequest,
    controller: v1Controller = Depends(get_controller)
):
    return await controller.create_user(request)
```

### 2. Implement handler in `controller/v1Controller.py`

```python
async def create_user(self, request: UserRequest) -> Result:
    # Business logic
    result = await self.repository.create_user(request)
    return result
```

### 3. Define schemas in `schema/schemas.py`

```python
class UserRequest(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

## Logging

This template includes a dual logging system for different use cases:

### Simple Logger (`logger`)

Use for application lifecycle events, debugging, and infrastructure operations:

```python
from config.logger import logger

logger.info("Application started")
logger.debug("Loading configuration")
logger.error("Error occurred", exc_info=True)
```

### Structured Logger (`structured_logger`)

Use for business events, HTTP requests, and anything requiring production queries:

```python
from config.logger import structured_logger

# Set persistent context for related logs
structured_logger.set_context(
    request_id="abc-123",
    user_id=456
)

# Log with additional fields
structured_logger.info(
    "Order created",
    order_id=789,
    amount=99.99,
    event_type="order_created"
)

# Always clear context when done
structured_logger.clear_context()
```

### When to Use Each

- **Use `logger`**: Startup/shutdown, config loading, cache operations, debug messages
- **Use `structured_logger`**: Authentication, CRUD operations, HTTP requests, business events

### Log Files

- Development: `./logs/YYYY-MM-DD/template_api.log`
- Production: `/var/log/app/logs/YYYY-MM-DD/template_api.log`
- Daily rotation with automatic folder creation at midnight
- Thread-safe for Uvicorn workers

## Middleware

### Compression Middleware (Enabled by default)

Automatically compresses large responses using gzip:

```python
app.add_middleware(
    CompressionMiddleware,
    min_size=500,           # Minimum size in bytes to compress
    compression_level=6,    # Compression level (1-9)
    exclude_paths=["/health", "/docs"]
)
```

### Rate Limiter (Optional)

Protects against abuse and DDoS attacks:

```python
# Uncomment in main.py to enable
app.add_middleware(
    RateLimiterMiddleware,
    max_requests=100,
    window_seconds=60
)
```

## Docker

### Build

```bash
docker build -t api-template .
```

### Run

```bash
# Environment variables from repositorio_lib
docker run -p 8000:8000 \
  -v $(pwd)/../repositorio_lib:/app/repositorio_lib \
  --env-file ../repositorio_lib/config/.env \
  api-template
```

## Integration with Shared Repository

This template **requires** a shared library (data layer) to function.

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
# Configuration (DO NOT use environment variables directly)
from repositorio_lib.config.settings import db_settings, jwt_settings, app_settings, api_settings

# Core infrastructure
from repositorio_lib.core.database import get_async_session
from repositorio_lib.core import setup_logger, log_performance

# Data access
from repositorio_lib.service.repository import v1Repository

# Logging (in your template)
from config.logger import logger, structured_logger

# Usage examples
db_url = db_settings.get_connection_string(async_mode=True)
secret_key = jwt_settings.SECRET_KEY
log_dir = app_settings.get_log_dir()
rate_limit = api_settings.RATE_LIMIT_REQUESTS
```

## Testing

```bash
pytest tests/ -v
```

## Production

### Environment Variables

**⚠️ CONFIGURE IN:** `repositorio_lib/config/.env`

Important variables for production:
- `ENVIRONMENT=production`
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME` (real credentials)
- `SECRET_KEY` (generate secure key)
- `LOG_DIR_PRD=/var/log/app/logs`
- `SMTP_*` (email configuration)
- `POOL_SIZE`, `MAX_OVERFLOW` (optimize for production)

### Run with Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production Recommendations

1. Use a reverse proxy (Nginx, Traefik)
2. Enable HTTPS
3. Configure CORS with specific origins
4. Enable rate limiting
5. Configure logging to files or external service
6. Implement monitoring (Prometheus, DataDog)
7. Use environment variables for secrets
8. Configure health checks in orchestrator (Kubernetes, Docker Swarm)

## Security

- JWT for authentication
- Configurable CORS
- Rate limiting against abuse
- Data validation with Pydantic
- Security headers (optional with SecurityHeadersMiddleware)

## License

Free code template for use in Python projects
