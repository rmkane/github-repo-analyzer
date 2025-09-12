"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from github_repo_analyzer.config import (
    APIConfig,
    CacheConfig,
    Config,
    LimitConfig,
    LoggingConfig,
    OutputConfig,
    create_config,
    get_config,
)


class TestConfigClasses:
    """Test cases for configuration dataclasses."""

    def test_cache_config_defaults(self):
        """Test CacheConfig default values."""
        cache = CacheConfig()
        assert cache.directory == ".cache"
        assert cache.ttl_seconds == 3600
        assert cache.enabled is True

    def test_api_config_defaults(self):
        """Test APIConfig default values."""
        api = APIConfig()
        assert api.timeout_seconds == 30
        assert api.max_retries == 3
        assert api.retry_delay_seconds == 1.0
        assert api.rate_limit_buffer == 10

    def test_limit_config_defaults(self):
        """Test LimitConfig default values."""
        limits = LimitConfig()
        assert limits.default_limit == 100
        assert limits.max_limit == 10000
        assert limits.unlimited_value == -1

    def test_output_config_defaults(self):
        """Test OutputConfig default values."""
        output = OutputConfig()
        assert output.default_format == "table"
        assert output.max_table_width == 120
        assert output.json_indent == 2
        assert output.summary_languages_count == 5

    def test_logging_config_defaults(self):
        """Test LoggingConfig default values."""
        logging = LoggingConfig()
        assert logging.level == "INFO"
        assert logging.format == "%(message)s"
        assert logging.stream == "stderr"


class TestConfig:
    """Test cases for main Config class."""

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_config_initialization_with_token(self):
        """Test Config initialization with token from environment."""
        config = Config()
        assert config.github_token == "test_token"
        assert isinstance(config.cache, CacheConfig)
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.limits, LimitConfig)
        assert isinstance(config.output, OutputConfig)
        assert isinstance(config.logging, LoggingConfig)

    def test_config_initialization_without_token(self):
        """Test Config initialization without token raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GitHub token is required"):
                Config()

    def test_config_validation_cache_ttl_negative(self):
        """Test Config validation with negative cache TTL."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            config = Config()
            config.cache.ttl_seconds = -1
            with pytest.raises(ValueError, match="Cache TTL must be non-negative"):
                config._validate()

    def test_config_validation_timeout_negative(self):
        """Test Config validation with negative timeout."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            config = Config()
            config.api.timeout_seconds = 0
            with pytest.raises(ValueError, match="API timeout must be positive"):
                config._validate()

    def test_config_validation_default_limit_negative(self):
        """Test Config validation with negative default limit."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            config = Config()
            config.limits.default_limit = 0
            with pytest.raises(ValueError, match="Default limit must be positive"):
                config._validate()

    def test_config_validation_max_limit_too_small(self):
        """Test Config validation with max limit smaller than default."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            config = Config()
            config.limits.max_limit = 50
            config.limits.default_limit = 100
            with pytest.raises(
                ValueError, match="Max limit must be greater than default limit"
            ):
                config._validate()

    def test_with_cache_disabled(self):
        """Test with_cache_disabled method."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            config = Config()
            disabled_config = config.with_cache_disabled()
            assert disabled_config.cache.enabled is False
            assert disabled_config.github_token == config.github_token
            assert disabled_config.api == config.api

    def test_with_custom_cache(self):
        """Test with_custom_cache method."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            config = Config()
            custom_config = config.with_custom_cache("/tmp/cache", 7200)
            assert custom_config.cache.directory == "/tmp/cache"
            assert custom_config.cache.ttl_seconds == 7200
            assert custom_config.cache.enabled is True

    def test_with_custom_token(self):
        """Test with_custom_token method."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            config = Config()
            custom_config = config.with_custom_token("custom_token")
            assert custom_config.github_token == "custom_token"
            assert config.github_token == "test_token"  # Original unchanged


class TestConfigFunctions:
    """Test cases for configuration functions."""

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_get_config(self):
        """Test get_config function."""
        config = get_config()
        assert isinstance(config, Config)
        assert config.github_token == "test_token"

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_create_config_default(self):
        """Test create_config with default parameters."""
        config = create_config()
        assert config.github_token == "test_token"
        assert config.cache.directory == ".cache"
        assert config.cache.enabled is True

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_create_config_custom_token(self):
        """Test create_config with custom token."""
        config = create_config(token="custom_token")
        assert config.github_token == "custom_token"

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_create_config_custom_cache(self):
        """Test create_config with custom cache settings."""
        config = create_config(cache_dir="/tmp/cache", cache_ttl=7200)
        assert config.cache.directory == "/tmp/cache"
        assert config.cache.ttl_seconds == 7200
        assert config.cache.enabled is True

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_create_config_no_cache(self):
        """Test create_config with caching disabled."""
        config = create_config(no_cache=True)
        assert config.cache.enabled is False

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_create_config_custom_timeout(self):
        """Test create_config with custom timeout."""
        config = create_config(timeout=60)
        assert config.api.timeout_seconds == 60
        assert config.api.max_retries == 3  # Other settings unchanged

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_create_config_combined_settings(self):
        """Test create_config with multiple custom settings."""
        config = create_config(
            token="custom_token",
            cache_dir="/tmp/cache",
            cache_ttl=7200,
            timeout=60,
            no_cache=False,
        )
        assert config.github_token == "custom_token"
        assert config.cache.directory == "/tmp/cache"
        assert config.cache.ttl_seconds == 7200
        assert config.cache.enabled is True
        assert config.api.timeout_seconds == 60
