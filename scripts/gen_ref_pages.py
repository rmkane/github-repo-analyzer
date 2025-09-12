"""Generate API reference pages for MkDocs."""

from pathlib import Path
from mkdocs_gen_files import Nav

nav = Nav()

# Define the modules to document
modules = [
    "github_repo_analyzer.core",
    "github_repo_analyzer.config",
    "github_repo_analyzer.validation",
    "github_repo_analyzer.loggers",
    "github_repo_analyzer.formatters",
    "github_repo_analyzer.utils",
    "github_repo_analyzer.commands",
]

# Generate API reference pages
for module in modules:
    # Create the markdown file
    doc_path = f"api/{module.split('.')[-1]}.md"

    # Add to navigation
    nav[doc_path] = module.split(".")[-1].title()

    # Generate the content
    content = f"""# {module.split('.')[-1].title()}

::: {module}
"""

    # Write the file
    with open(f"docs/{doc_path}", "w") as f:
        f.write(content)

# Write the navigation
with open("docs/api/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
