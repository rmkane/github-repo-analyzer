"""Tests for the validation module."""

import pytest

from github_repo_analyzer.validation import (
    ValidationError,
    validate_analyze_inputs,
    validate_cache_dir,
    validate_cache_ttl,
    validate_config_inputs,
    validate_github_token,
    validate_language,
    validate_limit,
    validate_min_forks,
    validate_min_stars,
    validate_output_format,
    validate_search_inputs,
    validate_sort_field,
    validate_username_or_org,
    validate_visibility_flags,
)


class TestValidationError:
    """Test cases for ValidationError class."""

    def test_validation_error_with_field(self):
        """Test ValidationError with field name."""
        error = ValidationError("Test error", "test_field")
        assert str(error) == "Test error"
        assert error.field == "test_field"

    def test_validation_error_without_field(self):
        """Test ValidationError without field name."""
        error = ValidationError("Test error")
        assert str(error) == "Test error"
        assert error.field is None


class TestValidateUsernameOrOrg:
    """Test cases for validate_username_or_org function."""

    def test_valid_usernames(self):
        """Test valid usernames."""
        valid_names = [
            "user123",
            "my-org",
            "test_user",
            "a",  # Minimum length
            "a" * 39,  # Maximum length
        ]

        for name in valid_names:
            result = validate_username_or_org(name)
            assert result == name.strip()

    def test_empty_username(self):
        """Test empty username."""
        with pytest.raises(ValidationError) as exc_info:
            validate_username_or_org("")
        assert exc_info.value.field == "username_or_org"

    def test_whitespace_only_username(self):
        """Test whitespace-only username."""
        with pytest.raises(ValidationError) as exc_info:
            validate_username_or_org("   ")
        assert exc_info.value.field == "username_or_org"

    def test_username_too_long(self):
        """Test username exceeding 39 characters."""
        long_name = "a" * 40
        with pytest.raises(ValidationError) as exc_info:
            validate_username_or_org(long_name)
        assert exc_info.value.field == "username_or_org"

    def test_username_invalid_characters(self):
        """Test usernames with invalid characters."""
        invalid_names = [
            "user@name",  # Special characters
            "user.name",  # Dots
            "-username",  # Starts with hyphen
            "username-",  # Ends with hyphen
            "user--name",  # Consecutive hyphens
        ]

        for name in invalid_names:
            with pytest.raises(ValidationError) as exc_info:
                validate_username_or_org(name)
            assert exc_info.value.field == "username_or_org"

    def test_username_strips_whitespace(self):
        """Test that usernames are stripped of whitespace."""
        result = validate_username_or_org("  testuser  ")
        assert result == "testuser"


class TestValidateLimit:
    """Test cases for validate_limit function."""

    def test_valid_limits(self):
        """Test valid limit values."""
        valid_limits = [None, -1, 0, 1, 100, 1000]

        for limit in valid_limits:
            result = validate_limit(limit)
            assert result == limit

    def test_invalid_limits(self):
        """Test invalid limit values."""
        invalid_limits = [-2, -10, -100]

        for limit in invalid_limits:
            with pytest.raises(ValidationError) as exc_info:
                validate_limit(limit)
            assert exc_info.value.field == "limit"

    def test_custom_field_name(self):
        """Test custom field name in error message."""
        with pytest.raises(ValidationError) as exc_info:
            validate_limit(-5, "custom_field")
        assert exc_info.value.field == "custom_field"


class TestValidateVisibilityFlags:
    """Test cases for validate_visibility_flags function."""

    def test_valid_combinations(self):
        """Test valid flag combinations."""
        valid_combinations = [
            (False, False),
            (True, False),
            (False, True),
        ]

        for public_only, private_only in valid_combinations:
            # Should not raise
            validate_visibility_flags(public_only, private_only)

    def test_invalid_combination(self):
        """Test invalid flag combination."""
        with pytest.raises(ValidationError) as exc_info:
            validate_visibility_flags(True, True)
        assert exc_info.value.field == "visibility_flags"


class TestValidateLanguage:
    """Test cases for validate_language function."""

    def test_valid_languages(self):
        """Test valid programming languages."""
        valid_languages = [
            "Python",
            "JavaScript",
            "C++",
            "C#",
            "Go",
            "Rust",
            "TypeScript",
            "HTML/CSS",
            "Shell",
            None,
            "",
            "   ",  # Whitespace only
        ]

        for lang in valid_languages:
            result = validate_language(lang)
            if lang and lang.strip():
                assert result == lang.strip().title()
            else:
                assert result is None

    def test_language_too_long(self):
        """Test language name exceeding 50 characters."""
        long_lang = "a" * 51
        with pytest.raises(ValidationError) as exc_info:
            validate_language(long_lang)
        assert exc_info.value.field == "language"

    def test_language_invalid_characters(self):
        """Test language names with invalid characters."""
        invalid_languages = [
            "Python@",
            "JavaScript!",
            "C++$",
        ]

        for lang in invalid_languages:
            with pytest.raises(ValidationError) as exc_info:
                validate_language(lang)
            assert exc_info.value.field == "language"


class TestValidateMinStars:
    """Test cases for validate_min_stars function."""

    def test_valid_min_stars(self):
        """Test valid minimum stars values."""
        valid_values = [None, 0, 1, 10, 100, 1000, 1000000]

        for value in valid_values:
            result = validate_min_stars(value)
            assert result == value

    def test_invalid_min_stars(self):
        """Test invalid minimum stars values."""
        invalid_values = [-1, -10, 1000001]

        for value in invalid_values:
            with pytest.raises(ValidationError) as exc_info:
                validate_min_stars(value)
            assert exc_info.value.field == "min_stars"


class TestValidateMinForks:
    """Test cases for validate_min_forks function."""

    def test_valid_min_forks(self):
        """Test valid minimum forks values."""
        valid_values = [None, 0, 1, 10, 100, 1000, 100000]

        for value in valid_values:
            result = validate_min_forks(value)
            assert result == value

    def test_invalid_min_forks(self):
        """Test invalid minimum forks values."""
        invalid_values = [-1, -10, 100001]

        for value in invalid_values:
            with pytest.raises(ValidationError) as exc_info:
                validate_min_forks(value)
            assert exc_info.value.field == "min_forks"


class TestValidateSortField:
    """Test cases for validate_sort_field function."""

    def test_valid_sort_fields(self):
        """Test valid sort fields."""
        valid_fields = ["name", "stars", "forks", "updated", "created", "size"]

        for field in valid_fields:
            result = validate_sort_field(field)
            assert result == field

    def test_invalid_sort_field(self):
        """Test invalid sort field."""
        with pytest.raises(ValidationError) as exc_info:
            validate_sort_field("invalid_field")
        assert exc_info.value.field == "sort_field"


class TestValidateOutputFormat:
    """Test cases for validate_output_format function."""

    def test_valid_output_formats(self):
        """Test valid output formats."""
        valid_formats = ["table", "json", "summary"]

        for format_type in valid_formats:
            result = validate_output_format(format_type)
            assert result == format_type

    def test_invalid_output_format(self):
        """Test invalid output format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_output_format("invalid_format")
        assert exc_info.value.field == "output_format"


class TestValidateCacheTtl:
    """Test cases for validate_cache_ttl function."""

    def test_valid_cache_ttl(self):
        """Test valid cache TTL values."""
        valid_values = [0, 1, 3600, 86400, 86400 * 30]  # Up to 30 days

        for value in valid_values:
            result = validate_cache_ttl(value)
            assert result == value

    def test_invalid_cache_ttl(self):
        """Test invalid cache TTL values."""
        invalid_values = [-1, -10, 86400 * 31]  # Negative or over 30 days

        for value in invalid_values:
            with pytest.raises(ValidationError) as exc_info:
                validate_cache_ttl(value)
            assert exc_info.value.field == "cache_ttl"


class TestValidateCacheDir:
    """Test cases for validate_cache_dir function."""

    def test_valid_cache_dirs(self):
        """Test valid cache directories."""
        valid_dirs = [".cache", "/tmp/cache", "~/cache", "cache"]

        for cache_dir in valid_dirs:
            result = validate_cache_dir(cache_dir)
            assert result == cache_dir.strip()

    def test_invalid_cache_dirs(self):
        """Test invalid cache directories."""
        invalid_dirs = ["", "   ", "a" * 501]  # Empty or too long

        for cache_dir in invalid_dirs:
            with pytest.raises(ValidationError) as exc_info:
                validate_cache_dir(cache_dir)
            assert exc_info.value.field == "cache_dir"


class TestValidateGithubToken:
    """Test cases for validate_github_token function."""

    def test_valid_tokens(self):
        """Test valid GitHub tokens."""
        valid_tokens = [
            "ghp_" + "a" * 36,  # Fine-grained token
            "gho_" + "a" * 36,  # OAuth token
            "a" * 40,  # Classic token
            "a" * 20,  # Minimum length
            "a" * 200,  # Maximum length
        ]

        for token in valid_tokens:
            result = validate_github_token(token)
            assert result == token.strip()

    def test_invalid_tokens(self):
        """Test invalid GitHub tokens."""
        invalid_tokens = ["", "   ", "a" * 19, "a" * 201]  # Too short or too long

        for token in invalid_tokens:
            with pytest.raises(ValidationError) as exc_info:
                validate_github_token(token)
            assert exc_info.value.field == "github_token"


class TestValidateAnalyzeInputs:
    """Test cases for validate_analyze_inputs function."""

    def test_valid_analyze_inputs(self):
        """Test valid analyze inputs."""
        inputs = {
            "username_or_org": "testuser",
            "limit": 100,
            "sort_field": "stars",
            "output_format": "table",
        }

        result = validate_analyze_inputs(**inputs)
        assert result["username_or_org"] == "testuser"
        assert result["limit"] == 100
        assert result["sort_field"] == "stars"
        assert result["output_format"] == "table"

    def test_invalid_analyze_inputs(self):
        """Test invalid analyze inputs."""
        with pytest.raises(ValidationError):
            validate_analyze_inputs("", 100, "stars", "table")  # Empty username


class TestValidateSearchInputs:
    """Test cases for validate_search_inputs function."""

    def test_valid_search_inputs(self):
        """Test valid search inputs."""
        inputs = {
            "username_or_org": "testuser",
            "limit": 50,
            "sort_field": "forks",
            "language": "Python",
            "min_stars": 10,
            "min_forks": 5,
            "public_only": True,
            "private_only": False,
        }

        result = validate_search_inputs(**inputs)
        assert result["username_or_org"] == "testuser"
        assert result["language"] == "Python"
        assert result["min_stars"] == 10
        assert result["public_only"] is True

    def test_invalid_search_inputs(self):
        """Test invalid search inputs."""
        with pytest.raises(ValidationError):
            validate_search_inputs(
                "testuser", 100, "stars", None, None, None, True, True
            )  # Both public_only and private_only


class TestValidateConfigInputs:
    """Test cases for validate_config_inputs function."""

    def test_valid_config_inputs(self):
        """Test valid config inputs."""
        inputs = {
            "token": "ghp_" + "a" * 36,
            "cache_dir": ".cache",
            "cache_ttl": 3600,
        }

        result = validate_config_inputs(**inputs)
        assert result["token"] == inputs["token"]
        assert result["cache_dir"] == ".cache"
        assert result["cache_ttl"] == 3600

    def test_config_inputs_without_token(self):
        """Test config inputs without token."""
        inputs = {
            "cache_dir": ".cache",
            "cache_ttl": 3600,
        }

        result = validate_config_inputs(**inputs)
        assert "token" not in result
        assert result["cache_dir"] == ".cache"
        assert result["cache_ttl"] == 3600

    def test_invalid_config_inputs(self):
        """Test invalid config inputs."""
        with pytest.raises(ValidationError):
            validate_config_inputs(cache_dir="", cache_ttl=3600)  # Empty cache dir
