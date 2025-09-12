"""Professional logging configuration for GitHub Repository Analyzer."""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from github_repo_analyzer.config import LoggingConfig


def get_default_log_dir() -> Path:
    """Get platform-appropriate default log directory.

    Returns:
        Path to the log directory following platform conventions:
        - Windows: %APPDATA%\\github-repo-analyzer\\logs
        - macOS: ~/Library/Logs/github-repo-analyzer
        - Linux: ~/.github-repo-analyzer/logs
    """
    if sys.platform == "win32":
        # Windows: %APPDATA%\github-repo-analyzer\logs
        appdata = os.environ.get("APPDATA", "")
        if not appdata:
            # Fallback to user profile if APPDATA not set
            appdata = os.environ.get("USERPROFILE", "") + "\\AppData\\Roaming"
        base_dir = Path(appdata) / "github-repo-analyzer" / "logs"
    elif sys.platform == "darwin":
        # macOS: ~/Library/Logs/github-repo-analyzer
        base_dir = Path.home() / "Library" / "Logs" / "github-repo-analyzer"
    else:
        # Linux/Unix: ~/.github-repo-analyzer/logs
        base_dir = Path.home() / ".github-repo-analyzer" / "logs"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_default_log_file() -> str:
    """Get default log file path with date-based naming.

    Returns:
        Path to today's log file
    """
    log_dir = get_default_log_dir()
    date_str = datetime.now().strftime("%Y-%m-%d")
    return str(log_dir / f"github-repo-analyzer-{date_str}.log")


def cleanup_old_logs(log_dir: Path, max_files: int = 7) -> None:
    """Remove log files older than max_files days.

    Args:
        log_dir: Directory containing log files
        max_files: Maximum number of log files to keep
    """
    try:
        log_files = sorted(log_dir.glob("github-repo-analyzer-*.log"))
        if len(log_files) > max_files:
            for old_log in log_files[:-max_files]:
                old_log.unlink()
    except Exception:
        # Silently ignore cleanup errors
        pass


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize formatter with color support detection."""
        super().__init__(*args, **kwargs)
        self._colors_enabled = self._supports_color()

    def _supports_color(self) -> bool:
        """Check if terminal supports colors."""
        # Check if we're in a TTY
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False

        # Check environment variables
        if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
            return False

        # Check if FORCE_COLOR is set
        if os.environ.get("FORCE_COLOR"):
            return True

        # Default to True for most modern terminals
        return True

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        if self._colors_enabled and record.levelname in self.COLORS:
            # Create a copy of the record to avoid modifying the original
            record_copy = logging.LogRecord(
                record.name,
                record.levelno,
                record.pathname,
                record.lineno,
                record.msg,
                record.args,
                record.exc_info,
            )
            record_copy.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
            # Copy other attributes
            for key, value in record.__dict__.items():
                if key not in (
                    "name",
                    "levelno",
                    "pathname",
                    "lineno",
                    "msg",
                    "args",
                    "exc_info",
                    "levelname",
                ):
                    setattr(record_copy, key, value)
            return super().format(record_copy)

        return super().format(record)


def setup_logging(
    config: Optional[LoggingConfig] = None,
    log_file: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False,
    no_auto_log: bool = False,
) -> logging.Logger:
    """Set up professional logging configuration.

    Args:
        config: Logging configuration (uses default if None)
        log_file: Optional log file path (overrides auto-logging)
        verbose: Enable verbose logging (DEBUG level)
        quiet: Enable quiet logging (WARNING level and above)
        no_auto_log: Disable automatic log file creation

    Returns:
        Configured logger instance
    """
    if config is None:
        config = LoggingConfig()

    # Determine log level based on flags
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = getattr(logging, config.level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("github_repo_analyzer")
    logger.setLevel(level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatters (always colored for console)
    console_formatter: logging.Formatter = ColoredFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # File formatter (more detailed)
    file_formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(
        sys.stdout if config.stream == "stdout" else sys.stderr
    )
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (automatic or specified)
    actual_log_file = None
    if log_file:
        # User specified a custom log file
        actual_log_file = log_file
    elif config.auto_log_file and not no_auto_log:
        # Automatic logging enabled
        actual_log_file = get_default_log_file()

    if actual_log_file:
        log_path = Path(actual_log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Rotating file handler (10MB max, keep 5 files)
        file_handler = logging.handlers.RotatingFileHandler(
            actual_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",  # 10MB
        )
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Cleanup old log files if using automatic logging
        if not log_file and config.auto_log_file:
            cleanup_old_logs(log_path.parent, config.max_log_files)

    # Prevent duplicate logs from propagating to root logger
    logger.propagate = False

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (uses 'github_repo_analyzer' if None)

    Returns:
        Logger instance
    """
    if name is None:
        name = "github_repo_analyzer"
    elif not name.startswith("github_repo_analyzer"):
        name = f"github_repo_analyzer.{name}"

    return logging.getLogger(name)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs: Any) -> None:
    """Log function call with parameters.

    Args:
        logger: Logger instance
        func_name: Function name
        **kwargs: Function parameters to log
    """
    if logger.isEnabledFor(logging.DEBUG):
        params = ", ".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
        logger.debug("Calling %s(%s)", func_name, params)


def log_performance(logger: logging.Logger, operation: str, duration: float) -> None:
    """Log performance metrics.

    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
    """
    if duration < 1.0:
        logger.debug("Performance: %s completed in %.3fs", operation, duration)
    elif duration < 5.0:
        logger.info("Performance: %s completed in %.3fs", operation, duration)
    else:
        logger.warning("Performance: %s took %.3fs (slow)", operation, duration)


def log_api_call(
    logger: logging.Logger, method: str, url: str, status_code: Optional[int] = None
) -> None:
    """Log API call details.

    Args:
        logger: Logger instance
        method: HTTP method
        url: API URL
        status_code: HTTP status code (if available)
    """
    if status_code:
        if 200 <= status_code < 300:
            logger.debug("API: %s %s -> %d", method, url, status_code)
        elif 400 <= status_code < 500:
            logger.warning("API: %s %s -> %d (client error)", method, url, status_code)
        else:
            logger.error("API: %s %s -> %d (server error)", method, url, status_code)
    else:
        logger.debug("API: %s %s", method, url)


def log_error_with_context(
    logger: logging.Logger, error: Exception, context: str = ""
) -> None:
    """Log error with additional context.

    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context information
    """
    context_msg = f" in {context}" if context else ""
    logger.error("Error%s: %s: %s", context_msg, type(error).__name__, error)
    logger.debug("Full traceback%s:", context_msg, exc_info=True)
