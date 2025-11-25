"""Exception Handlers for Web"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

# Centralized loggers
from config.logger import logger, structured_logger

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(404)
    async def not_found(request: Request, exc):
        # Log 404 errors with structured logger
        structured_logger.warning(
            "Page not found",
            path=str(request.url.path),
            method=request.method,
            status_code=404,
            event_type="http_error"
        )

        # TODO: Render 404.html template
        return HTMLResponse("<h1>404 - Page not found</h1>", status_code=404)

    @app.exception_handler(500)
    async def server_error(request: Request, exc):
        logger.error(f"Error 500: {exc}", exc_info=True)

        # Log 500 errors with structured logger
        structured_logger.error(
            "Internal server error",
            path=str(request.url.path),
            method=request.method,
            error=str(exc),
            status_code=500,
            event_type="http_error"
        )

        return HTMLResponse("<h1>500 - Server error</h1>", status_code=500)
