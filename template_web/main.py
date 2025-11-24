"""
Web Template - Main Entry Point

Template for web applications with FastAPI + Jinja2.
Combines backend API with HTML template rendering.

Usage:
    uvicorn main:app --port 8000 --reload
"""

# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Other
from contextlib import asynccontextmanager
import logging

# Centralized logger (ONE logger for the entire application)
from config.logger import logger

# Exception handlers
from exception.exception_handlers import register_exception_handlers

# Project
from router import v1Router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the web application lifecycle.
    Initializes resources on startup and cleans up on shutdown.
    """
    logger.info("Web application started and ready")

    # TODO: Add initialization if needed
    # - Database connection
    # - Data preloading
    # - Cache initialization

    yield

    logger.info("Shutting down web application...")


# Create FastAPI application
app = FastAPI(
    title="Web Template",
    description="Template for web applications with FastAPI + Jinja2",
    version="v1.0.0",
    contact={
        "name": "Support",
        "email": "support@example.com",
    },
    lifespan=lifespan,
    # Customize docs URL if needed
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Register exception handlers
register_exception_handlers(app)


# region Middlewares

# CORS to allow requests from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# endregion


# region Static Files and Templates

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Make templates available globally for routers
app.state.templates = templates

# endregion


# region Routes

# Include routers
app.include_router(v1Router.router, prefix="", tags=["web"])

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
