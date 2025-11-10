"""
API Template - Main Entry Point

Generic template for creating REST APIs with FastAPI.
Includes JWT authentication, compression middleware, rate limiting, and centralized logging.

Usage:
    uvicorn main:app --port 8000 --reload
"""

# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Other
from contextlib import asynccontextmanager
import logging

# Environment
import config.env as env

# Repository (uncomment when you have your shared library configured)
# from your_repo_lib.utils import retry_until_success
# from your_repo_lib.config.settings import api_settings
# from your_repo_lib.core.logger import setup_logger

# Exception handlers
from exception.exception_handlers import register_exception_handlers

# Middleware
from middleware.CompressionMiddleware import CompressionMiddleware
# from middleware.RateLimiterMiddleware import RateLimiterMiddleware

# Project
from router import v1Router

# TODO: Configure logger with your logging system
# Setup logger for API
# logger = setup_logger("api", level=logging.INFO, log_to_file=True)

# Temporary basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage FastAPI application lifecycle.
    Preloads reference data on startup and releases resources on shutdown.

    Customize this function to:
    - Preload static data (parameters, catalogs, etc.)
    - Establish connections to external services
    - Initialize cache
    - Initialize workers or connection pools
    """
    logger.info("🚀 API started and ready to receive requests")

    # TODO: Add data preloading
    # try:
    #     await retry_until_success(preload_parameters, name="parameters")
    #     logger.info("✅ Data preloaded successfully")
    # except Exception as e:
    #     logger.error(f"❌ Error during initialization: {e}", exc_info=True)

    yield

    logger.info("🛑 Closing application...")


# Create FastAPI application
app = FastAPI(
    title="API Template",
    description="Generic template for creating REST APIs with FastAPI",
    version="v1.0.0",
    contact={
        "name": "Support Team",
        "email": "support@yourcompany.com",
    },
    lifespan=lifespan,
)

# Register centralized exception handlers
register_exception_handlers(app)


# region Middlewares
# IMPORTANT: Middleware registration order matters
# They execute in reverse order of registration (last registered = first to execute)

# CORS must be last (first to execute) to handle preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression middleware: automatically compresses large responses
app.add_middleware(
    CompressionMiddleware,
    min_size=500,           # Minimum size in bytes to compress
    compression_level=6,    # Gzip compression level (1-9)
    exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"]
)

# TODO: Uncomment rate limiter if you need it
# Rate limiter: protects against abuse and DDoS
# app.add_middleware(
#     RateLimiterMiddleware,
#     max_requests=100,
#     window_seconds=60
# )

# endregion


# region Routes

# Include main router with /api/v1 prefix
app.include_router(v1Router.router, prefix="/api/v1", tags=["api"])


@app.get("/")
def read_root():
    """Root endpoint - basic API information"""
    return {
        "status": "running",
        "message": "API Template is active",
        "version": "v1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and orchestrators (Kubernetes, Docker Swarm, etc.)

    Returns:
        dict: Health status of the API and its dependencies
    """
    return {
        "status": "healthy",
        "database": "not_configured",  # TODO: Verify real database connection
        "cache": "not_configured",     # TODO: Verify Redis/cache connection if applicable
        "environment": env.APP_ENV.get("environment", "unknown")
    }

# endregion


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
