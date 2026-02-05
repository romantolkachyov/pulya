#!/usr/bin/env bash
set -euo pipefail

date_str=$(date +"%Y-%m-%d %H:%M:%S")
git_commit=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
python_version=$(python --version 2>&1)

# Define BASELINE_DIR and DATE if not already set
: ${DATE:=$(date +%Y%m%d-%H%M)}
BASELINE_DIR="performance-reports/baselines"
mkdir -p "${BASELINE_DIR}"

# Create markdown report header
cat > "${BASELINE_DIR}/baseline-${DATE}.md" << EOF
# Performance Baseline Report

**Date:** ${date_str}
**Git Commit:** ${git_commit}
**Python:** ${python_version}

## Benchmark Results

\("""
EOF
