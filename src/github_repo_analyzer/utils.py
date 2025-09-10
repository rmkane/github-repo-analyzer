"""Utility functions for GitHub Repository Analyzer."""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def clean_repository_data(repos_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean control characters from repository data.

    Args:
        repos_data: List of repository dictionaries from GitHub API

    Returns:
        List of cleaned repository dictionaries
    """
    logger.debug("Cleaning %d repositories", len(repos_data))
    cleaned_repos = []
    for repo in repos_data:
        cleaned_repo = {}
        for key, value in repo.items():
            if isinstance(value, str):
                # Replace control characters with spaces
                original_value = value
                cleaned_repo[key] = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", value)
                # Collapse multiple spaces
                cleaned_repo[key] = re.sub(r"\s+", " ", cleaned_repo[key]).strip()
                if original_value != cleaned_repo[key]:
                    logger.debug("Cleaned control characters in %s", key)
            else:
                cleaned_repo[key] = value
        cleaned_repos.append(cleaned_repo)
    logger.debug("Cleaned %d repositories", len(cleaned_repos))
    return cleaned_repos
