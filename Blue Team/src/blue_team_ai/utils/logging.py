from __future__ import annotations

import logging
from logging.config import dictConfig
from typing import Any, Dict

import structlog
import os
from pathlib import Path


def configure_logging(level: str = "INFO") -> None:
    logging_level = logging.getLevelName(level.upper())
    # Ensure a file-backed logs directory exists (used for audit/security JSONL)
    logs_dir = Path(os.getenv("LOG_DIR", "./logs")).resolve()
    logs_dir.mkdir(parents=True, exist_ok=True)
    audit_log_path = str((logs_dir / "audit.jsonl").resolve())
    security_log_path = str((logs_dir / "security.jsonl").resolve())
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "plain": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "foreign_pre_chain": [
                        structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.add_log_level,
                        structlog.processors.StackInfoRenderer(),
                    ],
                    "processor": structlog.dev.ConsoleRenderer(colors=False),
                },
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "foreign_pre_chain": [
                        structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.add_log_level,
                        structlog.processors.StackInfoRenderer(),
                    ],
                    "processor": structlog.processors.JSONRenderer(),
                },
            },
            "handlers": {
                "default": {
                    "level": logging_level,
                    "class": "logging.StreamHandler",
                    "formatter": "plain",
                },
                "audit_file": {
                    "level": logging_level,
                    "class": "logging.FileHandler",
                    "filename": audit_log_path,
                    "mode": "a",
                    "encoding": "utf-8",
                    "formatter": "json",
                },
                "security_file": {
                    "level": logging_level,
                    "class": "logging.FileHandler",
                    "filename": security_log_path,
                    "mode": "a",
                    "encoding": "utf-8",
                    "formatter": "json",
                },
            },
            "loggers": {
                # Root logger -> console
                "": {"handlers": ["default"], "level": logging_level},
                # Structured audit and security streams -> console + JSONL files
                "audit": {
                    "handlers": ["default", "audit_file"],
                    "level": logging_level,
                    "propagate": False,
                },
                "security": {
                    "handlers": ["default", "security_file"],
                    "level": logging_level,
                    "propagate": False,
                },
            },
        }
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def audit_log(event: str, **details: Any) -> None:
    logger = get_logger("audit")
    logger.info(event, **_sanitize(details))


def security_log(event: str, severity: str = "info", **details: Any) -> None:
    logger = get_logger("security")
    log_method = getattr(logger, severity.lower(), logger.info)
    log_method(event, **_sanitize(details))


def _sanitize(details: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {}
    for key, value in details.items():
        if "password" in key.lower() or "secret" in key.lower():
            sanitized[key] = "***REDACTED***"
        else:
            sanitized[key] = value
    return sanitized

