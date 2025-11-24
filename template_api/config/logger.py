"""
Centralized Logger - Template API

This module configures and exports the single application logger.
ALL modules must import the logger from here.

Usage in any module:
    from config.logger import logger

    logger.info("Log message")
    logger.error("Error occurred", exc_info=True)
"""

import logging

# Uncomment when you have repositorio_lib installed
# from repositorio_lib.core.logger import setup_logger
# logger = setup_logger("template_api", level=logging.INFO, log_to_file=True)

# Basic temporary logger (until you install repositorio_lib)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("template_api")

__all__ = ["logger"]
