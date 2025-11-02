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


def get_logger(name: str | None = None):
    """
    Get a logger instance, optionally bound to a specific name.

    Args:
        name: Optional name to bind to the logger (e.g., module name)

    Returns:
        Logger instance (loguru logger)

    Note:
        Loguru uses a single global logger instance, so the name parameter
        is provided for API compatibility but doesn't create separate loggers.
        The actual module name is automatically captured by loguru.
    """
    return logger
