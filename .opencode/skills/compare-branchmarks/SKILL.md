# Compare Benchmarks Skill

## Overview
This skill provides instructions for comparing benchmark JSON files without loading entire files into context.

## Problem
Benchmark JSON files can be very large (MBs) and exceed agent context limits.

## Solution: Streaming Comparison with jq

### Prerequisites
Ensure `jq` is installed:
```bash
# macOS
brew install jq

# Ubuntu/Debian
apt-get install jq

# Or use uv to run it
uv tool install jq
```

### Step 1: Check File Size
Always check file size before reading:
```bash
ls -lh performance-reports/baselines/*.json performance-reports/results/*.json
```

If files are >100KB, use streaming approach below.

### Step 2: Extract Key Metrics
Extract only the metrics you need:

```bash
# Extract benchmark names and mean times
jq '.benchmarks[] | {name: .name, mean: .stats.mean}' performance-reports/results/current.json

# Extract specific benchmark
jq '.benchmarks[] | select(.name == "test_static_route_benchmark") | {name: .name, mean: .stats.mean, median: .stats.median}' performance-reports/results/current.json

# Compare two files - extract both
jq -n \
  --argfile baseline performance-reports/baselines/baseline-20260206.json \
  --argfile current performance-reports/results/current-20260207.json \
  '
  $baseline.benchmarks[] as $b |
  $current.benchmarks[] as $c |
  select($b.name == $c.name) |
  {
    name: $b.name,
    baseline_mean: $b.stats.mean,
    current_mean: $c.stats.mean,
    change_pct: (($c.stats.mean - $b.stats.mean) / $b.stats.mean * 100)
  }
  '
```

### Step 3: Generate Comparison Report
Create a markdown comparison:

```bash
jq -n \
  --argfile baseline performance-reports/baselines/baseline.json \
  --argfile current performance-reports/results/current.json \
  '
  "# Benchmark Comparison Report\n\n",
  "| Benchmark | Baseline (ns) | Current (ns) | Change % |\n",
  "|-----------|---------------|--------------|----------|\n",
  (
    $baseline.benchmarks[] as $b |
    $current.benchmarks[] as $c |
    select($b.name == $c.name) |
    "| \($b.name) | \($b.stats.mean | floor) | \($c.stats.mean | floor) | \((($c.stats.mean - $b.stats.mean) / $b.stats.mean * 100) | round)\n"
  )
  ' > reports/benchmark-comparison.md
```

### Step 4: Justfile Integration
Add to justfile:

```just
# Compare benchmark results
compare-benchmarks baseline current:
    @echo "Comparing benchmarks..."
    jq -n \
      --argfile baseline {{baseline}} \
      --argfile current {{current}} \
      '
      $baseline.benchmarks[] as $b |
      $current.benchmarks[] as $c |
      select($b.name == $c.name) |
      {
        name: $b.name,
        baseline_mean: $b.stats.mean,
        current_mean: $c.stats.mean,
        change_pct: (($c.stats.mean - $b.stats.mean) / $b.stats.mean * 100)
      }
      '

# List available benchmark files
list-benchmarks:
    @echo "Baseline files:"
    @ls -lh performance-reports/baselines/*.json 2>/dev/null || echo "  No baseline files found"
    @echo ""
    @echo "Result files:"
    @ls -lh performance-reports/results/*.json 2>/dev/null || echo "  No result files found"
```

## Usage Example

```bash
# List available benchmarks
just list-benchmarks

# Compare specific files
just compare-benchmarks performance-reports/baselines/baseline-20260206.json performance-reports/results/current-20260207.json
```

## Important Notes

1. **Never read large JSON files directly** - Always use jq to extract specific fields
2. **Check file sizes first** - Use `ls -lh` before any read operation
3. **Stream processing** - jq processes files line by line, keeping memory usage low
4. **Selective extraction** - Extract only the metrics you need for comparison
5. **File naming** - Use consistent naming: baseline-YYYYMMDD.json, current-YYYYMMDD.json
