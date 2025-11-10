"""
Configuración de variables de entorno globales

Este módulo maneja la carga y almacenamiento de variables de entorno
para el servicio de consola.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Diccionario global para almacenar configuración
APP_ENV = {
    # Timestamp de inicio
    "timestamp": datetime.now().isoformat(),

    # Configuración básica
    "environment": os.getenv("ENVIRONMENT", "dev"),

    # Configuración del servicio
    "intervalo_minutos": int(os.getenv("MINUTOS_CONSOLA", "60")),
    "modo_continuo": os.getenv("ENABLE_CONTINUOUS_MODE", "true").lower() == "true",
    "max_reintentos": int(os.getenv("MAX_RETRIES", "3")),

    # Métricas de ejecución
    "total_ciclos": 0,
    "ciclos_exitosos": 0,
    "ciclos_fallidos": 0,
    "ultimo_ciclo": None,
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


def increment_ciclo():
    """Incrementa contador de ciclos totales"""
    APP_ENV["total_ciclos"] += 1


def increment_exitoso():
    """Incrementa contador de ciclos exitosos"""
    APP_ENV["ciclos_exitosos"] += 1
    APP_ENV["ultimo_ciclo"] = datetime.now().isoformat()


def increment_fallido():
    """Incrementa contador de ciclos fallidos"""
    APP_ENV["ciclos_fallidos"] += 1


def get_metricas() -> dict:
    """
    Obtiene métricas de ejecución del servicio.

    Returns:
        Diccionario con métricas
    """
    return {
        "total_ciclos": APP_ENV["total_ciclos"],
        "ciclos_exitosos": APP_ENV["ciclos_exitosos"],
        "ciclos_fallidos": APP_ENV["ciclos_fallidos"],
        "ultimo_ciclo": APP_ENV["ultimo_ciclo"],
        "tasa_exito": (
            APP_ENV["ciclos_exitosos"] / APP_ENV["total_ciclos"]
            if APP_ENV["total_ciclos"] > 0
            else 0
        )
    }
