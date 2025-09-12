"""Summary formatter for GitHub Repository Analyzer."""

from typing import Any, Dict

from rich.console import Console
from rich.panel import Panel

console = Console()


def display_summary(stats: Dict[str, Any], username_or_org: str, is_org: bool) -> None:
    """Display repository statistics in a summary format.

    Args:
        stats: Dictionary containing repository statistics
        username_or_org: Username or organization name
        is_org: Whether the input is an organization
    """
    if not stats:
        console.print("[red]No statistics available.[/red]")
        return

    # Extract statistics
    total_repos = stats.get("total_repositories", 0)
    total_stars = stats.get("total_stars", 0)
    total_forks = stats.get("total_forks", 0)
    total_size = stats.get("total_size", 0)
    languages = stats.get("languages", {})
    private_count = stats.get("private_count", 0)
    archived_count = stats.get("archived_count", 0)

    # Create summary text
    entity_type = "Organization" if is_org else "User"
    summary_text = f"""
[bold cyan]Repository Summary for {entity_type}: {username_or_org}[/bold cyan]

[bold]📊 Statistics:[/bold]
• Total Repositories: [yellow]{total_repos}[/yellow]
• Total Stars: [yellow]{total_stars:,}[/yellow]
• Total Forks: [yellow]{total_forks:,}[/yellow]
• Total Size: [yellow]{total_size:.1f} MB[/yellow]
• Private Repositories: [red]{private_count}[/red]
• Archived Repositories: [dim]{archived_count}[/dim]

[bold]💻 Top Languages:[/bold]
"""

    # Add top languages
    if languages:
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        for lang, count in sorted_languages[:5]:  # Top 5 languages
            summary_text += f"• {lang}: [green]{count}[/green] repositories\n"
    else:
        summary_text += "• No language data available\n"

    # Create and display panel
    panel = Panel(
        summary_text.strip(),
        title="📈 Repository Analysis Summary",
        border_style="blue",
        padding=(1, 2),
    )

    console.print(panel)
