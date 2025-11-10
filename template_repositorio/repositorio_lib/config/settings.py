"""
Settings centralizados con Pydantic

Carga y valida todas las variables de entorno necesarias.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class DatabaseSettings(BaseSettings):
    """Configuración de base de datos"""
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str

    class Config:
        env_file = ".env"


class JWTSettings(BaseSettings):
    """Configuración de JWT"""
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    class Config:
        env_file = ".env"


class AppSettings(BaseSettings):
    """Configuración general de la aplicación"""
    ENVIRONMENT: str = "dev"
    LOG_DIR_DEV: str = "logs"
    LOG_DIR_EXTERNAL: str = "/var/log/app/logs"

    class Config:
        env_file = ".env"

    def get_log_dir(self) -> str:
        """Retorna directorio de logs según entorno"""
        return self.LOG_DIR_DEV if self.ENVIRONMENT == "dev" else self.LOG_DIR_EXTERNAL


# Instancias globales de configuración
db_settings = DatabaseSettings()
jwt_settings = JWTSettings()
app_settings = AppSettings()
