# GitHub Repository Analyzer Makefile

.PHONY: help install install-dev build test lint format clean run docker-build docker-run

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install the package in production mode
	python3 -m venv venv
	venv/bin/pip install .

install-dev: ## Install the package in development mode with all dependencies
	python3 -m venv venv
	venv/bin/pip install -e ".[dev]"

# Build targets
build: ## Build the package
	python3 -m build

build-wheel: ## Build wheel distribution
	python3 -m build --wheel

build-sdist: ## Build source distribution
	python3 -m build --sdist

# Development targets
test: ## Run tests
	venv/bin/pytest

test-cov: ## Run tests with coverage
	venv/bin/pytest --cov=src/github_repo_analyzer --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	venv/bin/pytest tests/test_api.py

test-integration: ## Run integration tests (requires GITHUB_TOKEN)
	venv/bin/pytest tests/test_cli.py

lint: ## Run linting checks
	venv/bin/flake8 src/github_repo_analyzer tests
	venv/bin/mypy src/github_repo_analyzer

format: ## Format code with isort and black
	venv/bin/isort src/github_repo_analyzer tests
	venv/bin/black src/github_repo_analyzer tests

format-check: ## Check code formatting
	venv/bin/isort --check-only src/github_repo_analyzer tests
	venv/bin/black --check src/github_repo_analyzer tests

# Setup development environment
setup-dev: ## Set up development environment
	python3 -m venv venv
	venv/bin/pip install -e ".[dev]"
	venv/bin/pre-commit install

# Cleanup targets
clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run targets
run: ## Run the CLI tool (example: make run ARGS="analyze microsoft --org")
	github-repo-analyzer $(ARGS)

run-dev: ## Run the CLI tool in development mode
	venv/bin/python -m github_repo_analyzer.cli $(ARGS)

# Docker targets
docker-build: ## Build Docker image
	docker build -t github-repo-analyzer .

docker-run: ## Run Docker container (example: make docker-run ARGS="analyze microsoft --org")
	docker run --rm -e GITHUB_TOKEN=$(GITHUB_TOKEN) github-repo-analyzer $(ARGS)

docker-shell: ## Run interactive shell in Docker container
	docker run --rm -it -e GITHUB_TOKEN=$(GITHUB_TOKEN) github-repo-analyzer /bin/bash

# Documentation targets
docs: ## Generate documentation with MkDocs
	venv/bin/python scripts/gen_ref_pages.py
	venv/bin/mkdocs build

docs-serve: ## Serve documentation locally
	venv/bin/python scripts/gen_ref_pages.py
	venv/bin/mkdocs serve

docs-deploy: ## Deploy documentation to GitHub Pages
	venv/bin/python scripts/gen_ref_pages.py
	venv/bin/mkdocs gh-deploy

docs-install: ## Install documentation dependencies
	venv/bin/pip install -e ".[docs]"

# Release targets
check-release: ## Check if ready for release
	python3 -m build --check
	twine check dist/*

release-test: ## Upload to TestPyPI
	twine upload --repository testpypi dist/*

release: ## Upload to PyPI
	twine upload dist/*

# Environment setup
env-example: ## Create example environment file
	@echo "GITHUB_TOKEN=your_github_token_here" > .env.example
	@echo "Created .env.example file"

# All-in-one targets
all: clean install-dev test lint format ## Run all checks (clean, install-dev, test, lint, format)

ci: install-dev test lint format-check ## Run CI pipeline locally
