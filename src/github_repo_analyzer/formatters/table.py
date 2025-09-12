"""Table formatter for GitHub Repository Analyzer."""

from typing import List

from rich.console import Console
from rich.table import Table

from github_repo_analyzer.core import Repository

console = Console()


def display_table(repos: List[Repository], username_or_org: str, is_org: bool) -> None:
    """Display repositories in a table format.

    Args:
        repos: List of Repository objects to display
        username_or_org: Username or organization name
        is_org: Whether the input is an organization
    """
    if not repos:
        console.print("[red]No repositories found.[/red]")
        return

    # Create table
    entity_type = "Organization" if is_org else "User"
    table = Table(title=f"Repositories for {entity_type}: {username_or_org}")

    # Add columns
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Language", style="magenta")
    table.add_column("Stars", justify="right", style="yellow")
    table.add_column("Forks", justify="right", style="green")
    table.add_column("Size (MB)", justify="right", style="blue")
    table.add_column("Private", justify="center", style="red")
    table.add_column("Archived", justify="center", style="dim")
    table.add_column("Updated", style="dim")

    # Add rows
    for repo in repos:
        table.add_row(
            repo.name,
            repo.language or "N/A",
            str(repo.stargazers_count),
            str(repo.forks_count),
            f"{repo.size:.1f}",
            "✓" if repo.private else "✗",
            "✓" if repo.archived else "✗",
            repo.updated_at[:10],  # Extract date part from ISO string
        )

    console.print(table)
