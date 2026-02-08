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
    DATE=$(date +%Y%m%d-%H%M)
    REPORT_DIR="performance-reports"
    BASELINE_DIR="${REPORT_DIR}/baselines"

    mkdir -p "${BASELINE_DIR}"

    echo "Running benchmarks..."

    # Create markdown report with header
    echo "# Performance Baseline Report" > "${BASELINE_DIR}/baseline-${DATE}.md"
    echo "" >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo "**Date:** $(date '+%Y-%m-%d %H:%M:%S')" >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo "**Git Commit:** $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo "**Python:** $(python --version 2>&1)" >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo "" >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo "## Benchmark Results" >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo "" >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo '```' >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo "" >> "${BASELINE_DIR}/baseline-${DATE}.md"

    # Run benchmarks and append output
    uv run pytest benchmarks/ -v --benchmark-only --benchmark-storage="${BASELINE_DIR}" >> "${BASELINE_DIR}/baseline-${DATE}.md" 2>&1 || true

    # Close code block
    echo "" >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo '```' >> "${BASELINE_DIR}/baseline-${DATE}.md"

    echo ""
    echo "Benchmark complete! Report saved to:"
    echo "  - ${BASELINE_DIR}/baseline-${DATE}.md"

# Run benchmarks and compare against baseline
benchmark-compare:
    #!/usr/bin/env bash
    set -euo pipefail
    REPORT_DIR="performance-reports"
    BASELINE_DIR="${REPORT_DIR}/baselines"

    echo "Running benchmarks and comparing against baseline..."
    uv run pytest benchmarks/ --benchmark-only --benchmark-compare --benchmark-storage="${BASELINE_DIR}"

    echo ""
    echo "Comparison complete! Results compared against the latest baseline in ${BASELINE_DIR}"
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
check:
    test
    lint
    @echo "All checks passed!"

# Install development dependencies
dev-setup:
    uv pip install -e ".[dev]"
    uv run pre-commit install
