"""Logging setup and utilities for GitHub Repository Analyzer."""

from .setup import (
    ColoredFormatter,
    cleanup_old_logs,
    get_default_log_dir,
    get_default_log_file,
    get_logger,
    log_api_call,
    log_error_with_context,
    log_function_call,
    log_performance,
    setup_logging,
)

__all__ = [
    "ColoredFormatter",
    "cleanup_old_logs",
    "get_default_log_dir",
    "get_default_log_file",
    "get_logger",
    "log_api_call",
    "log_error_with_context",
    "log_function_call",
    "log_performance",
    "setup_logging",
]
