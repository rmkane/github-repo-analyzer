"""JSON formatter for GitHub Repository Analyzer."""

import json
from typing import List

from github_repo_analyzer.core import Repository


def display_json(repos: List[Repository]) -> None:
    """Display repositories in JSON format.

    Args:
        repos: List of Repository objects to display
    """
    if not repos:
        print("[]")
        return

    # Convert repositories to dictionaries
    repo_dicts = [repo.to_dict() for repo in repos]

    # Pretty print JSON
    print(json.dumps(repo_dicts, indent=2, default=str))
