"""Data models for GitHub Repository Analyzer."""

import hashlib
import logging
import pickle
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Repository(BaseModel):
    """Repository model."""

    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    clone_url: str
    ssh_url: str
    language: Optional[str] = None
    stargazers_count: int = Field(alias="stargazers_count")
    forks_count: int = Field(alias="forks_count")
    open_issues_count: int = Field(alias="open_issues_count")
    size: int
    created_at: str
    updated_at: str
    pushed_at: Optional[str] = None
    private: bool
    archived: bool
    disabled: bool
    topics: List[str] = Field(default_factory=list)
    license: Optional[Dict] = None
    owner: Dict


class CacheManager:
    """Simple file-based cache manager for API responses."""

    def __init__(self, cache_dir: Optional[str] = ".cache", ttl_seconds: int = 3600):
        """Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files (None to disable caching)
            ttl_seconds: Time-to-live for cached data in seconds (default: 1 hour)
        """
        self.cache_dir: Optional[Path] = (
            Path(cache_dir) if cache_dir is not None else None
        )
        if self.cache_dir is not None:
            self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.enabled = cache_dir is not None

    def _get_cache_key(self, url: str, params: Dict[str, Union[str, int]]) -> str:
        """Generate a cache key for the request."""
        # Create a hash of URL + sorted params for consistent keys
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        cache_string = f"{url}?{param_str}"
        return hashlib.md5(cache_string.encode()).hexdigest()

    def get(self, url: str, params: Dict[str, Union[str, int]]) -> Optional[List[Dict]]:
        """Get cached data if available and not expired."""
        if not self.enabled:
            return None

        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"  # type: ignore

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "rb") as f:
                cached_data: Dict[str, Any] = pickle.load(f)

            # Check if cache is expired
            if time.time() - cached_data["timestamp"] > self.ttl_seconds:
                logger.debug("Cache expired for %s", cache_key)
                cache_file.unlink()  # Remove expired cache
                return None

            logger.debug("Cache hit for %s", cache_key)
            return cached_data["data"]  # type: ignore

        except (pickle.PickleError, KeyError, OSError) as e:
            logger.warning("Failed to load cache file %s: %s", cache_file, e)
            cache_file.unlink()  # Remove corrupted cache
            return None

    def set(
        self, url: str, params: Dict[str, Union[str, int]], data: List[Dict]
    ) -> None:
        """Cache the response data."""
        if not self.enabled:
            return

        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"  # type: ignore

        try:
            cached_data = {
                "timestamp": time.time(),
                "data": data,
                "url": url,
                "params": params,
            }

            with open(cache_file, "wb") as f:
                pickle.dump(cached_data, f)

            logger.debug("Cached response for %s", cache_key)

        except OSError as e:
            logger.warning("Failed to save cache file %s: %s", cache_file, e)

    def clear(self) -> None:
        """Clear all cached data."""
        if self.enabled and self.cache_dir is not None and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            logger.debug("Cleared all cache files")
