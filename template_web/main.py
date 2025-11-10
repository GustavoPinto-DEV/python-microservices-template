"""
Web Template - Main Entry Point

Template para aplicaciones web con FastAPI + Jinja2.
Combina backend API con renderizado de templates HTML.

Uso:
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

# Environment
import config.env as env

# TODO: Descomentar cuando tengas repositorio_lib configurado
# from repositorio_lib.core.logger import setup_logger

# Exception handlers
from exception.exception_handlers import registrar_exception_handlers

# Project
from router import v1Router

# Setup logger
# logger = setup_logger("web", level=logging.INFO, log_to_file=True)

# Alternativa temporal sin repositorio_lib
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación web.
    Inicializa recursos al arrancar y limpia al cerrar.
    """
    logger.info("🚀 Aplicación web iniciada y lista")

    # TODO: Agregar inicialización si es necesaria
    # - Conexión a base de datos
    # - Precarga de datos
    # - Inicialización de caché

    yield

    logger.info("🛑 Cerrando aplicación web...")


# Crear aplicación FastAPI
app = FastAPI(
    title="Web Template",
    description="Template para aplicaciones web con FastAPI + Jinja2",
    version="v1.0.0",
    contact={
        "name": "Soporte",
        "email": "soporte@example.com",
    },
    lifespan=lifespan,
    # Personalizar docs URL si necesitas
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Registrar manejadores de excepciones
registrar_exception_handlers(app)


# region Middlewares

# CORS para permitir requests desde diferentes orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configurar orígenes específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# endregion


# region Static Files y Templates

# Montar archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates Jinja2
templates = Jinja2Templates(directory="templates")

# Hacer templates disponible globalmente para routers
app.state.templates = templates

# endregion


# region Routes

# Incluir routers
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
