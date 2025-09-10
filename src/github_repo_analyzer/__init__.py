"""GitHub Repository Analyzer - A CLI tool to analyze GitHub repositories."""

# Import version from package metadata
try:
    from importlib.metadata import version, metadata
    __version__ = version("github-repo-analyzer")
    meta = metadata("github-repo-analyzer")
    __author__ = meta.get("Author") or "Ryan Kane"
    email_raw = meta.get("Author-email") or "rmkane@users.noreply.github.com"
    # Extract just the email if it's in "Name <email>" format
    __email__ = email_raw.split("<")[-1].split(">")[0] if "<" in email_raw else email_raw
    __license__ = meta.get("License") or "MIT"
except Exception:
    # Fallback for development/editable installs
    __version__ = "0.1.0"
    __author__ = "Ryan Kane"
    __email__ = "rmkane@users.noreply.github.com"
    __license__ = "MIT"

__repository__ = "https://github.com/rmkane/github-repo-analyzer"
