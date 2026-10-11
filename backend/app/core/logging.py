"""
Structured logging configuration.
"""
import logging
import sys

import structlog

from app.core.config import get_settings

settings = get_settings()

try:
    from pythonjsonlogger import jsonlogger

    _HAS_JSON_LOGGER = True
except ImportError:
    _HAS_JSON_LOGGER = False


def configure_logging() -> None:
    """Configure structured logging for the application."""

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ExtraAdder(),
    ]

    if settings.APP_ENV == "development":
        shared_processors.append(structlog.dev.ConsoleRenderer())
    else:
        shared_processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_handler = logging.StreamHandler(sys.stdout)
    if _HAS_JSON_LOGGER:
        formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    log_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [log_handler]
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
