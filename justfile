# Pulya Framework Justfile
# https://github.com/casey/just

# Default recipe - list all available commands
default:
    @just --list

# Run all tests with coverage
test:
    uv run pytest --cov=pulya --cov-fail-under=100 -v

# Run linting and formatting checks
lint:
    uv run ruff check .
    uv run ruff format . --check
    uv run mypy src/pulya tests

# Fix all auto-fixable linting issues
fix:
    uv run ruff check . --fix
    uv run ruff format .

# Run pre-commit hooks on all files
pre-commit:
    uv run pre-commit run --all-files

# Run benchmarks and save results with timestamp
benchmark:
    #!/usr/bin/env bash
    set -euo pipefail
    DATE=$(date +%Y%m%d)
    REPORT_DIR="performance-reports"
    BASELINE_DIR="${REPORT_DIR}/baselines"

    echo "Running benchmarks..."
    uv run pytest benchmarks/ -v --benchmark-only

    echo ""
    echo "Benchmark complete! Results saved to:"
    echo "  - Markdown: ${BASELINE_DIR}/baseline-${DATE}.md"
    echo ""
    echo "To view baseline comparison, see:"
    echo "  - ${BASELINE_DIR}/BASELINE-2026-02-05.md"

# Run benchmarks and compare against baseline
benchmark-compare:
    #!/usr/bin/env bash
    set -euo pipefail
    DATE=$(date +%Y%m%d)
    REPORT_DIR="performance-reports"
    BASELINE_DIR="${REPORT_DIR}/baselines"

    echo "Running benchmarks and comparing against baseline..."
    uv run pytest benchmarks/ --benchmark-only --benchmark-compare --benchmark-json="${BASELINE_DIR}/baseline-${DATE}.json"

# Generate baseline report (one-time setup)
baseline:
    #!/usr/bin/env bash
    set -euo pipefail
    DATE=$(date +%Y%m%d)
    REPORT_DIR="performance-reports"
    BASELINE_DIR="${REPORT_DIR}/baselines"

    echo "Generating baseline performance report..."
    uv run pytest benchmarks/ --benchmark-only
    echo ""
    echo "Baseline saved. See ${BASELINE_DIR}/BASELINE.md for historical data."

# Build the package
build:
    uv build

# Clean build artifacts
clean:
    rm -rf dist/ build/ .ruff_cache/ .pytest_cache/ .mypy_cache/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Run all checks (tests, lint, coverage)
check: test lint
    @echo "All checks passed!"

# Install development dependencies
dev-setup:
    uv pip install -e ".[dev]"
    uv run pre-commit install
