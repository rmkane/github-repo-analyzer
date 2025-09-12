"""Input validation module for GitHub Repository Analyzer.

This module provides centralized validation functions for all user inputs,
ensuring consistent validation logic across the application.
"""

import re
from typing import Optional, Dict, Any

from github_repo_analyzer.logging_config import get_logger

logger = get_logger(__name__)


class ValidationError(ValueError):
    """Custom exception for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field: Field name that failed validation (optional)
        """
        super().__init__(message)
        self.field = field


def validate_username_or_org(username_or_org: str) -> str:
    """Validate GitHub username or organization name.

    Args:
        username_or_org: Username or organization name to validate

    Returns:
        Cleaned username or organization name

    Raises:
        ValidationError: If validation fails
    """
    if not username_or_org:
        raise ValidationError(
            "Username or organization name cannot be empty", "username_or_org"
        )

    # Strip whitespace
    cleaned = username_or_org.strip()

    if not cleaned:
        raise ValidationError(
            "Username or organization name cannot be empty", "username_or_org"
        )

    # GitHub username/org rules:
    # - Must be 1-39 characters
    # - Can contain alphanumeric characters, hyphens, and underscores
    # - Cannot start or end with a hyphen
    # - Cannot have consecutive hyphens

    if len(cleaned) > 39:
        raise ValidationError(
            "Username or organization name cannot exceed 39 characters",
            "username_or_org",
        )

    # Allow alphanumeric, hyphens, and underscores
    if not re.match(r"^[a-zA-Z0-9_-]+$", cleaned):
        raise ValidationError(
            "Username or organization name can only contain alphanumeric characters, "
            "hyphens, and underscores",
            "username_or_org",
        )

    # Check for invalid patterns
    if cleaned.startswith("-") or cleaned.endswith("-"):
        raise ValidationError(
            "Username or organization name cannot start or end with hyphens",
            "username_or_org",
        )

    if "--" in cleaned:
        raise ValidationError(
            "Username or organization name cannot have consecutive hyphens",
            "username_or_org",
        )

    logger.debug("Validated username/org: %s", cleaned)
    return cleaned


def validate_limit(limit: Optional[int], field_name: str = "limit") -> Optional[int]:
    """Validate limit parameter.

    Args:
        limit: Limit value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated limit value

    Raises:
        ValidationError: If validation fails
    """
    if limit is None:
        return None

    if limit < -1:
        raise ValidationError(
            f"{field_name} must be -1 (unlimited) or non-negative", field_name
        )

    logger.debug("Validated %s: %s", field_name, limit)
    return limit


def validate_visibility_flags(public_only: bool, private_only: bool) -> None:
    """Validate visibility filter flags.

    Args:
        public_only: Public only flag
        private_only: Private only flag

    Raises:
        ValidationError: If validation fails
    """
    if public_only and private_only:
        raise ValidationError(
            "Cannot specify both --public-only and --private-only flags",
            "visibility_flags",
        )

    logger.debug(
        "Validated visibility flags: public_only=%s, private_only=%s",
        public_only,
        private_only,
    )


def validate_language(language: Optional[str]) -> Optional[str]:
    """Validate programming language filter.

    Args:
        language: Programming language to validate

    Returns:
        Cleaned language name

    Raises:
        ValidationError: If validation fails
    """
    if not language:
        return None

    # Strip whitespace and normalize case
    cleaned = language.strip().title()

    if not cleaned:
        return None

    # Basic validation - language names should be reasonable
    if len(cleaned) > 50:
        raise ValidationError(
            "Programming language name cannot exceed 50 characters", "language"
        )

    # Allow alphanumeric, spaces, and common punctuation including forward slash
    if not re.match(r"^[a-zA-Z0-9\s\-\+\.\#\/]+$", cleaned):
        raise ValidationError(
            "Programming language name contains invalid characters", "language"
        )

    logger.debug("Validated language: %s", cleaned)
    return cleaned


def validate_min_stars(min_stars: Optional[int]) -> Optional[int]:
    """Validate minimum stars filter.

    Args:
        min_stars: Minimum stars value to validate

    Returns:
        Validated minimum stars value

    Raises:
        ValidationError: If validation fails
    """
    if min_stars is None:
        return None

    if min_stars < 0:
        raise ValidationError("Minimum stars must be non-negative", "min_stars")

    if min_stars > 1000000:  # Reasonable upper limit
        raise ValidationError("Minimum stars cannot exceed 1,000,000", "min_stars")

    logger.debug("Validated min_stars: %s", min_stars)
    return min_stars


def validate_min_forks(min_forks: Optional[int]) -> Optional[int]:
    """Validate minimum forks filter.

    Args:
        min_forks: Minimum forks value to validate

    Returns:
        Validated minimum forks value

    Raises:
        ValidationError: If validation fails
    """
    if min_forks is None:
        return None

    if min_forks < 0:
        raise ValidationError("Minimum forks must be non-negative", "min_forks")

    if min_forks > 100000:  # Reasonable upper limit
        raise ValidationError("Minimum forks cannot exceed 100,000", "min_forks")

    logger.debug("Validated min_forks: %s", min_forks)
    return min_forks


def validate_sort_field(sort_field: str) -> str:
    """Validate sort field parameter.

    Args:
        sort_field: Sort field to validate

    Returns:
        Validated sort field

    Raises:
        ValidationError: If validation fails
    """
    valid_fields = {"name", "stars", "forks", "updated", "created", "size"}

    if sort_field not in valid_fields:
        raise ValidationError(
            f"Sort field must be one of: {', '.join(sorted(valid_fields))}",
            "sort_field",
        )

    logger.debug("Validated sort_field: %s", sort_field)
    return sort_field


def validate_output_format(output_format: str) -> str:
    """Validate output format parameter.

    Args:
        output_format: Output format to validate

    Returns:
        Validated output format

    Raises:
        ValidationError: If validation fails
    """
    valid_formats = {"table", "json", "summary"}

    if output_format not in valid_formats:
        raise ValidationError(
            f"Output format must be one of: {', '.join(sorted(valid_formats))}",
            "output_format",
        )

    logger.debug("Validated output_format: %s", output_format)
    return output_format


def validate_cache_ttl(cache_ttl: int) -> int:
    """Validate cache TTL parameter.

    Args:
        cache_ttl: Cache TTL in seconds to validate

    Returns:
        Validated cache TTL

    Raises:
        ValidationError: If validation fails
    """
    if cache_ttl < 0:
        raise ValidationError("Cache TTL must be non-negative", "cache_ttl")

    if cache_ttl > 86400 * 30:  # 30 days max
        raise ValidationError(
            "Cache TTL cannot exceed 30 days (2,592,000 seconds)", "cache_ttl"
        )

    logger.debug("Validated cache_ttl: %s", cache_ttl)
    return cache_ttl


def validate_cache_dir(cache_dir: str) -> str:
    """Validate cache directory parameter.

    Args:
        cache_dir: Cache directory path to validate

    Returns:
        Cleaned cache directory path

    Raises:
        ValidationError: If validation fails
    """
    if not cache_dir:
        raise ValidationError("Cache directory cannot be empty", "cache_dir")

    cleaned = cache_dir.strip()

    if not cleaned:
        raise ValidationError("Cache directory cannot be empty", "cache_dir")

    # Basic path validation
    if len(cleaned) > 500:  # Reasonable path length limit
        raise ValidationError(
            "Cache directory path cannot exceed 500 characters", "cache_dir"
        )

    logger.debug("Validated cache_dir: %s", cleaned)
    return cleaned


def validate_github_token(token: str) -> str:
    """Validate GitHub token format.

    Args:
        token: GitHub token to validate

    Returns:
        Validated token

    Raises:
        ValidationError: If validation fails
    """
    if not token:
        raise ValidationError("GitHub token cannot be empty", "github_token")

    cleaned = token.strip()

    if not cleaned:
        raise ValidationError("GitHub token cannot be empty", "github_token")

    # GitHub tokens are typically 40 characters for classic tokens
    # or start with 'ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_' for fine-grained tokens
    if len(cleaned) < 20:
        raise ValidationError("GitHub token appears to be too short", "github_token")

    if len(cleaned) > 200:  # Reasonable upper limit
        raise ValidationError("GitHub token appears to be too long", "github_token")

    logger.debug("Validated GitHub token (length: %d)", len(cleaned))
    return cleaned


def validate_analyze_inputs(
    username_or_org: str,
    limit: Optional[int] = None,
    sort_field: str = "updated",
    output_format: str = "table",
) -> Dict[str, Any]:
    """Validate all inputs for the analyze command.

    Args:
        username_or_org: Username or organization name
        limit: Limit value
        sort_field: Sort field
        output_format: Output format

    Returns:
        Dictionary of validated inputs

    Raises:
        ValidationError: If any validation fails
    """
    logger.debug("Validating analyze command inputs")

    validated = {
        "username_or_org": validate_username_or_org(username_or_org),
        "limit": validate_limit(limit),
        "sort_field": validate_sort_field(sort_field),
        "output_format": validate_output_format(output_format),
    }

    logger.debug("All analyze inputs validated successfully")
    return validated


def validate_search_inputs(
    username_or_org: str,
    limit: Optional[int] = None,
    sort_field: str = "updated",
    language: Optional[str] = None,
    min_stars: Optional[int] = None,
    min_forks: Optional[int] = None,
    public_only: bool = False,
    private_only: bool = False,
) -> Dict[str, Any]:
    """Validate all inputs for the search command.

    Args:
        username_or_org: Username or organization name
        limit: Limit value
        sort_field: Sort field
        language: Programming language filter
        min_stars: Minimum stars filter
        min_forks: Minimum forks filter
        public_only: Public only flag
        private_only: Private only flag

    Returns:
        Dictionary of validated inputs

    Raises:
        ValidationError: If any validation fails
    """
    logger.debug("Validating search command inputs")

    # Validate visibility flags first
    validate_visibility_flags(public_only, private_only)

    validated = {
        "username_or_org": validate_username_or_org(username_or_org),
        "limit": validate_limit(limit),
        "sort_field": validate_sort_field(sort_field),
        "language": validate_language(language),
        "min_stars": validate_min_stars(min_stars),
        "min_forks": validate_min_forks(min_forks),
        "public_only": public_only,
        "private_only": private_only,
    }

    logger.debug("All search inputs validated successfully")
    return validated


def validate_config_inputs(
    token: Optional[str] = None,
    cache_dir: str = ".cache",
    cache_ttl: int = 3600,
) -> Dict[str, Any]:
    """Validate configuration inputs.

    Args:
        token: GitHub token
        cache_dir: Cache directory
        cache_ttl: Cache TTL in seconds

    Returns:
        Dictionary of validated inputs

    Raises:
        ValidationError: If any validation fails
    """
    logger.debug("Validating configuration inputs")

    validated = {
        "cache_dir": validate_cache_dir(cache_dir),
        "cache_ttl": validate_cache_ttl(cache_ttl),
    }

    if token:
        validated["token"] = validate_github_token(token)

    logger.debug("Configuration inputs validated successfully")
    return validated
