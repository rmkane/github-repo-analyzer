"""Analyze command for GitHub Repository Analyzer."""

from typing import Optional

import click
from rich.console import Console

from github_repo_analyzer.config import create_config
from github_repo_analyzer.core import GitHubAPI, RepositoryService
from github_repo_analyzer.formatters import display_json, display_summary, display_table
from github_repo_analyzer.loggers import get_logger
from github_repo_analyzer.utils import clamp_limit
from github_repo_analyzer.validation import (
    validate_analyze_inputs,
    validate_config_inputs,
    ValidationError,
)

logger = get_logger(__name__)
console = Console()


@click.command()
@click.argument("username_or_org")
@click.option("--org", is_flag=True, help="Treat the input as an organization name")
@click.option("--token", "-t", help="GitHub personal access token")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["table", "json", "summary"]),
    default="table",
    help="Output format (default: table)",
)
@click.option(
    "--limit",
    type=int,
    help="Limit number of repositories to show (default: 100, use -1 for all)",
)
@click.option(
    "--sort",
    "-s",
    type=click.Choice(["name", "stars", "forks", "updated", "created", "size"]),
    default="stars",
    help="Sort repositories by field (default: stars)",
)
@click.option(
    "--cache-dir", default=".cache", help="Directory for cache files (default: .cache)"
)
@click.option(
    "--cache-ttl",
    type=int,
    default=3600,
    help="Cache time-to-live in seconds (default: 3600)",
)
@click.option("--no-cache", is_flag=True, help="Disable caching")
@click.pass_context
def analyze(
    ctx: click.Context,
    username_or_org: str,
    org: bool,
    token: Optional[str],
    output: str,
    limit: Optional[int],
    sort: str,
    cache_dir: str,
    cache_ttl: int,
    no_cache: bool,
) -> None:
    """Analyze repositories for a GitHub user or organization.

    Args:
        ctx: Click context
        username_or_org: GitHub username or organization name
        org: Whether the input is an organization
        token: GitHub personal access token
        output: Output format (table, json, summary)
        limit: Maximum number of repositories to fetch
        sort: Sort repositories by field (name, stars, forks, updated, created, size)
        cache_dir: Cache directory
        cache_ttl: Cache time-to-live in seconds
        no_cache: Whether to disable caching
    """
    try:
        # Validate configuration inputs
        config_inputs = validate_config_inputs(
            token=token,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )

        # Create configuration
        config = create_config(
            token=config_inputs.get("token"),
            cache_dir=config_inputs["cache_dir"],
            cache_ttl=config_inputs["cache_ttl"],
            no_cache=no_cache,
        )

        # Validate analyze inputs
        analyze_inputs = validate_analyze_inputs(
            username_or_org=username_or_org,
            limit=limit,
            sort_field=sort,
            output_format=output,
        )

        # Initialize API and service
        api = GitHubAPI(
            token=config.github_token,
            cache_dir=config.cache.directory if config.cache.enabled else None,
            cache_ttl=config.cache.ttl_seconds,
            timeout=config.api.timeout_seconds,
        )
        service = RepositoryService(api)

        logger.info(
            "Fetching repositories for %s: %s",
            "organization" if org else "user",
            analyze_inputs["username_or_org"],
        )

        # Clamp limit to valid range using config
        limit_val = clamp_limit(
            analyze_inputs["limit"],
            config.limits.default_limit,
            config.limits.max_limit,
        )

        # Analyze repositories using service
        stats = service.analyze_repositories(
            analyze_inputs["username_or_org"],
            is_organization=org,
            limit=limit_val,
            sort_field=analyze_inputs["sort_field"],
        )

        if not stats:
            console.print("[red]No repositories found or error occurred.[/red]")
            return

        repos = stats["repositories"]

        if analyze_inputs["limit"]:
            repos = repos[: analyze_inputs["limit"]]

        if analyze_inputs["output_format"] == "summary":
            display_summary(stats, analyze_inputs["username_or_org"], org)
        elif analyze_inputs["output_format"] == "json":
            display_json(repos)
        else:
            display_table(repos, analyze_inputs["username_or_org"], org)

    except (ValueError, ValidationError) as e:
        error_msg = str(e)
        if "token" in error_msg.lower():
            console.print(f"[red]Authentication Error: {error_msg}[/red]")
            console.print(
                "[yellow]Tip: Set GITHUB_TOKEN environment variable or use "
                "--token option[/yellow]"
            )
        elif "rate limit" in error_msg.lower():
            console.print(f"[red]Rate Limit Error: {error_msg}[/red]")
            console.print(
                "[yellow]Tip: Wait a few minutes before trying again, or use a "
                "personal access token for higher limits[/yellow]"
            )
        elif "not found" in error_msg.lower():
            console.print(f"[red]Not Found Error: {error_msg}[/red]")
            console.print(
                "[yellow]Tip: Check the username or organization name is "
                "correct[/yellow]"
            )
        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            console.print(f"[red]Network Error: {error_msg}[/red]")
            console.print(
                "[yellow]Tip: Check your internet connection and try again[/yellow]"
            )
        else:
            console.print(f"[red]Error: {error_msg}[/red]")
        raise click.ClickException(error_msg)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        logger.exception("Unexpected error in analyze command")
        raise click.ClickException(f"Unexpected error: {e}")
