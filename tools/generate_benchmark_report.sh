#!/usr/bin/env bash
set -euo pipefail

date=$(date +%Y%m%d-%H%M)
report_dir="performance-reports"
baseline_dir="${report_dir}/baselines"

mkdir -p "${baseline_dir}"

echo "Running benchmarks..."

# Create markdown report with header
echo "# Performance Baseline Report" > "${baseline_dir}/baseline-${date}.md"
echo "" >> "${baseline_dir}/baseline-${date}.md"
echo "**Date:** $(date '+%Y-%m-%d %H:%M:%S')" >> "${baseline_dir}/baseline-${date}.md"
echo "**Git Commit:** $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" >> "${baseline_dir}/baseline-${date}.md"
echo "**Python:** $(python --version 2>&1)" >> "${baseline_dir}/baseline-${date}.md"
echo "" >> "${baseline_dir}/baseline-${date}.md"
echo "## Benchmark Results" >> "${baseline_dir}/baseline-${date}.md"
echo "" >> "${baseline_dir}/baseline-${date}.md"
echo '```' >> "${baseline_dir}/baseline-${date}.md"
echo "" >> "${baseline_dir}/baseline-${date}.md"

# Run benchmarks and append output
uv run pytest benchmarks/ --benchmark-only --benchmark-storage="${baseline_dir}" >> "${baseline_dir}/baseline-${date}.md" 2>&1 || true

# Close code block
echo "" >> "${baseline_dir}/baseline-${date}.md"
echo '```' >> "${baseline_dir}/baseline-${date}.md"

echo ""
echo "Benchmark complete! Report saved to:"
echo "  - ${baseline_dir}/baseline-${date}.md"
