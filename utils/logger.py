"""Logging configuration using loguru for voice agent platform."""

import os
import sys

from loguru import logger


def configure_logging() -> None:
    """
    Configure loguru logging with sensible defaults.

    Configures log level from LOG_LEVEL environment variable and sets up
    colored output to stdout.
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Remove default handler
    logger.remove()

    # Add custom handler with colorization and formatting
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level_str,
        colorize=True,
    )
