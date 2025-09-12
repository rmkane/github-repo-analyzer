"""Command-line interface for GitHub Repository Analyzer."""

from typing import Optional

import click
from dotenv import load_dotenv

# Import version information from package
from github_repo_analyzer import __version__
from github_repo_analyzer.commands import analyze, search, version
from github_repo_analyzer.loggers import get_logger, setup_logging

# Load environment variables
load_dotenv()

# Set up logging (will be reconfigured based on CLI flags)
logger = get_logger(__name__)


@click.group()
@click.version_option(version=__version__, prog_name="github-repo-analyzer")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all logging output")
@click.option("--log-file", help="Log to specific file (overrides automatic logging)")
@click.option("--no-auto-log", is_flag=True, help="Disable automatic log file creation")
@click.pass_context
def main(
    ctx: click.Context,
    verbose: bool,
    quiet: bool,
    log_file: Optional[str],
    no_auto_log: bool,
) -> None:
    """GitHub Repository Analyzer - A CLI tool to analyze GitHub repositories.

    This tool allows you to analyze repositories for GitHub users and organizations,
    providing insights into repository statistics, languages, activity, and more.

    Examples:
        github-repo-analyzer analyze rmkane
        github-repo-analyzer analyze microsoft --org --limit 50
        github-repo-analyzer search python --language python --min-stars 100
    """
    # Set up logging
    setup_logging(
        log_file=log_file,
        verbose=verbose,
        quiet=quiet,
        no_auto_log=no_auto_log,
    )

    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["log_file"] = log_file
    ctx.obj["no_auto_log"] = no_auto_log

    logger.info("GitHub Repository Analyzer started")


# Add commands to the main group
main.add_command(analyze)
main.add_command(search)
main.add_command(version)


if __name__ == "__main__":
    main()
