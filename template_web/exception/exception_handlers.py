"""Exception Handlers for Web"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

# Centralized logger
from config.logger import logger

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(404)
    async def not_found(request: Request, exc):
        # TODO: Render 404.html template
        return HTMLResponse("<h1>404 - Page not found</h1>", status_code=404)

    @app.exception_handler(500)
    async def server_error(request: Request, exc):
        logger.error(f"Error 500: {exc}", exc_info=True)
        return HTMLResponse("<h1>500 - Server error</h1>", status_code=500)
