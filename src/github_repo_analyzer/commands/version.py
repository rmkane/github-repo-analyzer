"""Version command for GitHub Repository Analyzer."""

import click
from rich.console import Console
from rich.panel import Panel

from github_repo_analyzer import (
    __author__,
    __email__,
    __license__,
    __repository__,
    __version__,
)

console = Console()


@click.command()
def version() -> None:
    """Show detailed version information."""
    version_info = f"""
[bold blue]GitHub Repository Analyzer[/bold blue]
Version: [green]{__version__}[/green]
Author: [yellow]{__author__}[/yellow]
Email: [cyan]{__email__}[/cyan]
Repository: [blue]{__repository__}[/blue]
License: [green]{__license__}[/green]
"""
    console.print(
        Panel(version_info.strip(), title="Version Information", border_style="blue")
    )
