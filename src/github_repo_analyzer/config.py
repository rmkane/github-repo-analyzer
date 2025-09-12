"""Configuration management for GitHub Repository Analyzer."""

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class CacheConfig:
    """Cache configuration settings."""

    directory: str = ".cache"
    ttl_seconds: int = 3600
    enabled: bool = True


@dataclass
class APIConfig:
    """GitHub API configuration settings."""

    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    rate_limit_buffer: int = 10  # Buffer before hitting rate limit


@dataclass
class LimitConfig:
    """Repository limit configuration settings."""

    default_limit: int = 100  # GitHub API max per page
    max_limit: int = 10000  # Maximum allowed limit
    unlimited_value: int = -1  # Value that means "unlimited"


@dataclass
class OutputConfig:
    """Output formatting configuration settings."""

    default_format: str = "table"
    max_table_width: int = 120
    json_indent: int = 2
    summary_languages_count: int = 5


@dataclass
class LoggingConfig:
    """Logging configuration settings."""

    level: str = "INFO"
    format: str = "%(message)s"
    stream: str = "stderr"  # stderr or stdout
    auto_log_file: bool = True  # Enable automatic log file creation
    max_log_files: int = 7  # Keep 7 days of log files


@dataclass
class Config:
    """Main configuration class for GitHub Repository Analyzer."""

    # GitHub API settings
    github_token: Optional[str] = field(
        default_factory=lambda: os.getenv("GITHUB_TOKEN")
    )

    # Sub-configurations
    cache: CacheConfig = field(default_factory=CacheConfig)
    api: APIConfig = field(default_factory=APIConfig)
    limits: LimitConfig = field(default_factory=LimitConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate configuration values."""
        if not self.github_token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN environment variable "
                "or pass token parameter."
            )

        if self.cache.ttl_seconds < 0:
            raise ValueError("Cache TTL must be non-negative")

        if self.api.timeout_seconds <= 0:
            raise ValueError("API timeout must be positive")

        if self.limits.default_limit <= 0:
            raise ValueError("Default limit must be positive")

        if self.limits.max_limit <= self.limits.default_limit:
            raise ValueError("Max limit must be greater than default limit")

    def with_cache_disabled(self) -> "Config":
        """Return a copy of config with caching disabled."""
        config = Config(
            github_token=self.github_token,
            cache=CacheConfig(enabled=False),
            api=self.api,
            limits=self.limits,
            output=self.output,
            logging=self.logging,
        )
        return config

    def with_custom_cache(self, directory: str, ttl_seconds: int) -> "Config":
        """Return a copy of config with custom cache settings."""
        config = Config(
            github_token=self.github_token,
            cache=CacheConfig(directory=directory, ttl_seconds=ttl_seconds),
            api=self.api,
            limits=self.limits,
            output=self.output,
            logging=self.logging,
        )
        return config

    def with_custom_token(self, token: str) -> "Config":
        """Return a copy of config with custom token."""
        config = Config(
            github_token=token,
            cache=self.cache,
            api=self.api,
            limits=self.limits,
            output=self.output,
            logging=self.logging,
        )
        return config


# Global configuration instance (lazy initialization)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance.

    Returns:
        Global configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def create_config(
    token: Optional[str] = None,
    cache_dir: Optional[str] = None,
    cache_ttl: Optional[int] = None,
    timeout: Optional[int] = None,
    no_cache: bool = False,
) -> Config:
    """Create a configuration with custom settings.

    Args:
        token: GitHub personal access token
        cache_dir: Cache directory path
        cache_ttl: Cache time-to-live in seconds
        timeout: API timeout in seconds
        no_cache: Whether to disable caching

    Returns:
        Custom configuration instance
    """
    # Start with global config
    global_config = get_config()
    custom_config = Config(
        github_token=token or global_config.github_token,
        cache=global_config.cache,
        api=global_config.api,
        limits=global_config.limits,
        output=global_config.output,
        logging=global_config.logging,
    )

    # Apply custom settings
    if cache_dir is not None or cache_ttl is not None or no_cache:
        cache_config = CacheConfig(
            directory=cache_dir or global_config.cache.directory,
            ttl_seconds=(
                cache_ttl if cache_ttl is not None else global_config.cache.ttl_seconds
            ),
            enabled=not no_cache,
        )
        custom_config.cache = cache_config

    if timeout is not None:
        api_config = APIConfig(
            timeout_seconds=timeout,
            max_retries=global_config.api.max_retries,
            retry_delay_seconds=global_config.api.retry_delay_seconds,
            rate_limit_buffer=global_config.api.rate_limit_buffer,
        )
        custom_config.api = api_config

    return custom_config
