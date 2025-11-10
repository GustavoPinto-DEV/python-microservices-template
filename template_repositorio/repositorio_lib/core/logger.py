"""
Sistema de logging centralizado
"""

import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
from repositorio_lib.config.settings import app_settings


def setup_logger(name: str, level=logging.INFO, log_to_file: bool = True):
    """
    Configura logger con rotación diaria.

    Args:
        name: Nombre del logger
        level: Nivel de logging
        log_to_file: Si debe escribir a archivo

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler con rotación
    if log_to_file:
        log_dir = Path(app_settings.get_log_dir())
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = TimedRotatingFileHandler(
            log_dir / f"{name}.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Logger por defecto
logger = setup_logger("repositorio_lib")
