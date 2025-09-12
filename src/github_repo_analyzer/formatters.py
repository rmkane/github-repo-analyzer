"""Output formatting utilities for GitHub Repository Analyzer."""

import json
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from github_repo_analyzer.core import Repository

console = Console()


def display_table(repos: List[Repository], username_or_org: str, is_org: bool) -> None:
    """Display repositories in a table format.

    Args:
        repos: List of Repository objects to display
        username_or_org: Username or organization name
        is_org: Whether the target is an organization
    """
    if not repos:
        console.print("[yellow]No repositories to display[/yellow]")
        return

    entity_type = "Organization" if is_org else "User"
    table = Table(title=f"Repositories for {entity_type}: {username_or_org}")

    # Add columns
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Language", style="magenta")
    table.add_column("Stars", justify="right", style="green")
    table.add_column("Forks", justify="right", style="blue")
    table.add_column("Size (MB)", justify="right", style="yellow")
    table.add_column("Private", justify="center")
    table.add_column("Archived", justify="center")
    table.add_column("Updated", style="dim")

    # Add rows
    for repo in repos:
        table.add_row(
            repo.name,
            repo.language or "N/A",
            str(repo.stargazers_count),
            str(repo.forks_count),
            f"{repo.size / 1024:.1f}",
            "✓" if repo.private else "✗",
            "✓" if repo.archived else "✗",
            repo.updated_at[:10] if repo.updated_at else "N/A",
        )

    console.print(table)


def display_json(repos: List[Repository]) -> None:
    """Display repositories in JSON format.

    Args:
        repos: List of Repository objects to display
    """
    # Convert repositories to dictionaries
    repo_dicts = [repo.to_dict() for repo in repos]
    print(json.dumps(repo_dicts, indent=2))


def display_summary(stats: Dict[str, Any], username_or_org: str, is_org: bool) -> None:
    """Display repository summary statistics.

    Args:
        stats: Dictionary containing repository statistics
        username_or_org: Username or organization name
        is_org: Whether the target is an organization
    """
    entity_type = "Organization" if is_org else "User"

    # Create summary panel
    summary_text = f"""
[bold cyan]{entity_type}:[/bold cyan] {username_or_org}

[bold green]Total Repositories:[/bold green] {stats.get('total_repositories', 0)}
[bold blue]Public:[/bold blue] {stats.get('public_repositories', 0)}
[bold red]Private:[/bold red] {stats.get('private_repositories', 0)}
[bold yellow]Archived:[/bold yellow] {stats.get('archived_repositories', 0)}

[bold green]Total Stars:[/bold green] {stats.get('total_stars', 0):,}
[bold blue]Total Forks:[/bold blue] {stats.get('total_forks', 0):,}
[bold yellow]Total Size:[/bold yellow] {stats.get('total_size_mb', 0):.1f} MB

[bold magenta]Top Languages:[/bold magenta]
"""

    # Add top languages
    top_languages = stats.get("top_languages", [])
    for lang, count in top_languages[:5]:  # Show top 5
        summary_text += f"  • {lang}: {count} repositories\n"

    panel = Panel(
        summary_text.strip(),
        title=f"Repository Summary - {username_or_org}",
        border_style="blue",
    )
    console.print(panel)
