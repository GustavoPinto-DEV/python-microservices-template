"""
Configuración de variables de entorno globales

Este módulo maneja la carga y almacenamiento de variables de entorno
que se usan a lo largo de toda la aplicación.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Diccionario global para almacenar configuración y datos precargados
APP_ENV = {
    # Timestamp de inicio
    "timestamp": datetime.now().isoformat(),

    # Configuración básica
    "environment": os.getenv("ENVIRONMENT", "dev"),

    # Aquí se pueden agregar datos precargados durante el lifespan
    # Por ejemplo:
    # "parametros": {},  # Datos precargados de parámetros
    # "catalogos": {},   # Catálogos de datos estáticos
    # "end_points": {},  # Endpoints registrados para auditoría
}


def get_env(key: str, default=None):
    """
    Obtiene una variable de entorno con un valor por defecto.

    Args:
        key: Nombre de la variable
        default: Valor por defecto si no existe

    Returns:
        Valor de la variable o default
    """
    return os.getenv(key, default)


def is_development() -> bool:
    """Verifica si estamos en entorno de desarrollo"""
    return APP_ENV.get("environment") == "dev"


def is_production() -> bool:
    """Verifica si estamos en entorno de producción"""
    return APP_ENV.get("environment") == "prd"
