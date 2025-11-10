"""Exception Handlers para Web"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import logging

logger = logging.getLogger(__name__)

def registrar_exception_handlers(app: FastAPI):
    @app.exception_handler(404)
    async def not_found(request: Request, exc):
        # TODO: Renderizar template 404.html
        return HTMLResponse("<h1>404 - Página no encontrada</h1>", status_code=404)

    @app.exception_handler(500)
    async def server_error(request: Request, exc):
        logger.error(f"Error 500: {exc}", exc_info=True)
        return HTMLResponse("<h1>500 - Error del servidor</h1>", status_code=500)
