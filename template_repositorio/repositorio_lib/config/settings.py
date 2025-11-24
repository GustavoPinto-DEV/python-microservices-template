"""
Centralized Settings with Pydantic

Loads and validates all necessary environment variables.
"""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

project_root = Path(__file__).parent.parent.parent.parent


class DefaultSettings(BaseSettings):
    """Default configuration"""

    class Config:
        env_file = Path(__file__).resolve().parent / ".env"


class DatabaseSettings(DefaultSettings):
    """Database configuration"""

    DB_USER: str = "root"
    DB_PASSWORD: str = "toor"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_ECHO: bool = False
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_PRE_PING: bool = False
    POOL_RECYCLE: int = 3600
    POOL_TIMEOUT: int = 30

    def get_connection_string(self, async_mode: bool = True) -> str:
        """
        Returns the PostgreSQL connection string.

        Args:
            async_mode: If True, uses the 'asyncpg' driver (for async SQLAlchemy)

        Returns:
            str: Complete connection string.
        """
        driver = "postgresql+asyncpg" if async_mode else "postgresql"
        return f"{driver}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class JWTSettings(DefaultSettings):
    """JWT configuration"""

    SECRET_KEY: str = "1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120


class AppSettings(DefaultSettings):
    """General application configuration"""

    ENVIRONMENT: str = "dev"
    LOG_DIR_DEV: Path = Field(default_factory=lambda: project_root / "logs")
    LOG_DIR_PRD: Path = Path("/var/log/app/logs")

    def get_log_dir(self) -> Path:
        """Returns log directory based on environment"""
        return self.LOG_DIR_DEV if self.ENVIRONMENT == "dev" else self.LOG_DIR_PRD


class EmailSettings(DefaultSettings):
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_OPERATIONS: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_PORT_TLS: int = 587
    SMTP_USE_SSL: bool = False
    SMTP_PORT_SSL: int = 465


# Global configuration instances
db_settings = DatabaseSettings()
jwt_settings = JWTSettings()
app_settings = AppSettings()
email_settings = EmailSettings()
