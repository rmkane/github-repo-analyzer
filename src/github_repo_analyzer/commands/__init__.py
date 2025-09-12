"""CLI commands for GitHub Repository Analyzer."""

from .analyze import analyze
from .search import search
from .version import version

__all__ = ["analyze", "search", "version"]
