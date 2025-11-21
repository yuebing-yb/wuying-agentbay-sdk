.PHONY: install test format build clean publish-test publish

# Get version from pyproject.toml
VERSION := $(shell poetry version -s)

# Install dependencies
install:
	@echo "Installing dependencies..."
	poetry install

# Run tests and formatting
test:
	@echo "Running tests..."
	poetry run python -m pytest tests/unit -v

# Format code
format:
	@echo "Formatting code..."
	poetry run black agentbay tests
	poetry run isort agentbay tests

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build dist *.egg-info
	@rm -rf .pytest_cache .coverage htmlcov
	@find . -type d -name __pycache__ -delete
	@find . -type f -name "*.pyc" -delete

# Generate sync code from async code
generate-sync:
	@echo "Generating sync code..."
	poetry run python scripts/generate_sync.py
	@echo "Generating sync examples..."
	poetry run python scripts/generate_examples_sync.py

# Build package
build: clean generate-sync format test
	@echo "Building package $(VERSION)..."
	poetry build

# Publish to Test PyPI
publish-test: build
	@echo "Publishing $(VERSION) to Test PyPI..."
	poetry config repositories.test-pypi https://test.pypi.org/legacy/
	poetry publish -r test-pypi

# Publish to PyPI
publish: build
	@echo "Publishing $(VERSION) to PyPI..."
	poetry publish