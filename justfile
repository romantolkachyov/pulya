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

# Benchmark stability settings: more rounds, no GC pauses during timing,
# warmup, and fixed hash seed for reproducible runs between processes.
export PYTHONHASHSEED := "0"
BENCH_FLAGS := "--benchmark-min-rounds=50 --benchmark-max-time=5.0 --benchmark-disable-gc --benchmark-warmup-iterations=100"

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
    uv run pytest benchmarks/ -v --benchmark-only {{ BENCH_FLAGS }} --benchmark-storage="${BASELINE_DIR}" >> "${BASELINE_DIR}/baseline-${DATE}.md" 2>&1 || true

    # Close code block
    echo "" >> "${BASELINE_DIR}/baseline-${DATE}.md"
    echo '```' >> "${BASELINE_DIR}/baseline-${DATE}.md"

    echo ""
    echo "Benchmark complete! Report saved to:"
    echo "  - ${BASELINE_DIR}/baseline-${DATE}.md"

# Run benchmarks and compare against baseline
benchmark-compare baseline="":
    #!/usr/bin/env bash
    set -euo pipefail
    REPORT_DIR="performance-reports"
    BASELINE_DIR="${REPORT_DIR}/baselines"
    CURRENT_JSON="${BASELINE_DIR}/current.json"

    # Pick the baseline: explicit argument > master.json (saved by
    # benchmark-baseline) > the latest baseline-*.json
    if [ -n "{{ baseline }}" ]; then
        BASELINE_JSON="{{ baseline }}"
    elif [ -f "${BASELINE_DIR}/master.json" ]; then
        BASELINE_JSON="${BASELINE_DIR}/master.json"
    else
        BASELINE_JSON=$(ls -1 "${BASELINE_DIR}"/baseline-*.json 2>/dev/null | sort | tail -1)
        if [ -z "${BASELINE_JSON}" ]; then
            echo "No baseline JSON found in ${BASELINE_DIR}. Run 'just benchmark-baseline' on master first." >&2
            exit 1
        fi
    fi

    echo "Running benchmarks..."
    uv run pytest benchmarks/ --benchmark-only {{ BENCH_FLAGS }} --benchmark-json="${CURRENT_JSON}" > /dev/null

    echo ""
    echo "Comparing against baseline: ${BASELINE_JSON}"
    uv run python tools/compare_benchmarks.py "${BASELINE_JSON}" "${CURRENT_JSON}"

# Save current benchmark results as the local reference baseline.
# Run on master before switching to a feature branch.
benchmark-baseline:
    #!/usr/bin/env bash
    set -euo pipefail
    BASELINE_DIR="performance-reports/baselines"
    mkdir -p "${BASELINE_DIR}"

    echo "Saving benchmark baseline (performance-reports/baselines/master.json)..."
    uv run pytest benchmarks/ --benchmark-only {{ BENCH_FLAGS }} --benchmark-json="${BASELINE_DIR}/master.json" > /dev/null
    echo "Baseline saved. Switch to your branch and run 'just benchmark-compare'."
# Generate baseline report (one-time setup)
baseline:
    #!/usr/bin/env bash
    set -euo pipefail
    DATE=$(date +%Y%m%d)
    REPORT_DIR="performance-reports"
    BASELINE_DIR="${REPORT_DIR}/baselines"

    echo "Generating baseline performance report..."
    uv run pytest benchmarks/ --benchmark-only {{ BENCH_FLAGS }}
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
