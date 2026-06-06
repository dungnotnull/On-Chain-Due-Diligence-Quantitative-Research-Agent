"""Structured logging with error taxonomy."""

from __future__ import annotations

import logging
import sys
from enum import StrEnum
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".cache" / "logs"


class ErrorCategory(StrEnum):
    DATA_VALIDATION = "data_validation"
    COLLECTOR_FAILURE = "collector_failure"
    API_RATE_LIMIT = "api_rate_limit"
    COST_CEILING = "cost_ceiling"
    INSUFFICIENT_DATA = "insufficient_data"
    CONFIG_ERROR = "config_error"
    INTERNAL_ERROR = "internal_error"


def setup_logging(
    level: str = "INFO",
    log_format: str = "structured",
    log_dir: str | Path | None = None,
) -> logging.Logger:
    """Configure structured or plain logging."""
    logger = logging.getLogger("chainlens")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    log_path = Path(log_dir or LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    if log_format == "structured":
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    else:
        fmt = "%(levelname)s: %(message)s"
    console.setFormatter(logging.Formatter(fmt))
    logger.addHandler(console)

    # File handler (always structured)
    file_handler = logging.FileHandler(
        log_path / "chainlens.log", encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    logger.addHandler(file_handler)

    return logger


def log_error(
    logger: logging.Logger,
    category: ErrorCategory,
    message: str,
    **extra: Any,
) -> None:
    """Log a structured error with category and metadata."""
    extras = " ".join(f"{k}={v}" for k, v in extra.items())
    logger.error("[%s] %s | %s", category.value, message, extras)


def log_warning(
    logger: logging.Logger,
    category: ErrorCategory,
    message: str,
    **extra: Any,
) -> None:
    extras = " ".join(f"{k}={v}" for k, v in extra.items())
    logger.warning("[%s] %s | %s", category.value, message, extras)
