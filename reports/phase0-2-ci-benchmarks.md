# CI Benchmarking Setup Report
## Phase 0-2: GitHub Actions Workflow for Performance Regression Detection

### Summary of Changes
- Added a new GitHub Actions workflow at `.github/workflows/benchmark.yml`
- Implemented performance regression detection logic that compares current benchmark results against baselines
- Set up the workflow to trigger on pushes to `master` and pull requests targeting `master`
- Configured the workflow to fail builds when performance degrades by more than 5%

### What Was Added to CI
**1. Benchmark Workflow File** (`/.github/workflows/benchmark.yml`):
- **Trigger**: Runs on pushes to `master` and pull requests targeting `master`
- **Environment**: Uses Python 3.12 on Ubuntu latest
- **Setup**:
  - Installs dependencies with `uv sync --locked --all-extras --dev`
  - Restores uv cache for faster builds
- **Benchmark Execution**:
  - Runs benchmarks using `uv run pytest benchmarks/ -v`
  - Stores results in a timestamped JSON file at `performance-reports/results/`
- **Regression Detection**:
  - Compares current results against the latest baseline in `performance-reports/baselines/`
  - Fails the build if any benchmark shows more than 5% performance degradation

**2. Performance Regression Logic**
The workflow implements the following regression detection:
- Loads current benchmark results from the executed test run
- Finds the latest baseline JSON file in `performance-reports/baselines/`
- Compares each benchmark metric (time, duration) between current and baseline
- Calculates percentage change: `(current - baseline) / baseline * 100`
- Fails the build if any metric shows >5% positive change (indicating performance degradation)

**3. Baseline Management**
- The workflow automatically uses the latest baseline file found in `performance-reports/baselines/`
- If no baselines exist, it skips comparison and continues with benchmark execution
- Baselines should be generated using the `just benchmark` command locally

### How Performance Regression Detection Works
**1. Baseline Establishment**
- Developers run `just benchmark` locally to generate baseline results
- These are stored in `performance-reports/baselines/` with timestamped filenames
- The first successful benchmark run establishes the initial baseline

**2. Comparison Process**
When a new code change is pushed:
1. The workflow runs benchmarks and generates current results
2. It automatically finds the latest baseline file in `performance-reports/baselines/`
3. For each benchmark test:
   - Compares metrics like execution time between current and baseline
   - Calculates percentage change: `(current - baseline) / baseline * 100`
   - If any metric increases by more than 5%, the workflow fails with a detailed message

**3. Example Output**
If a regression is detected, you'll see output like:
```
⚠️  Performance regression detected in test_large_json_serialization (time):
   Baseline: 61124.9998
   Current: 75000.0000
   Change: +22.69% (regression)
```

**4. Non-Regression Output**
If no regressions are found:
```
✓ No performance regressions detected
```

### How to Interpret Benchmark Results
**1. Understanding Metrics**
- **Min**: Fastest observed execution time (in nanoseconds)
- **Max**: Slowest observed execution time
- **Mean**: Average execution time across all runs
- **StdDev**: Standard deviation (measure of consistency)
- **Median**: Middle value when sorted by execution time
- **IQR**: Interquartile range (middle 50% of results)
- **OPS**: Operations per second (1 / Mean)

**2. Key Indicators**
- Look for significant changes in **Mean** and **Median** values
- High **StdDev** or large **IQR** may indicate inconsistent performance
- **Outliers** column shows tests that deviated significantly from the mean
- **OPS** is useful for comparing throughput between different runs

**3. Regression Thresholds**
- The workflow fails on >5% positive change in any metric
- This threshold can be adjusted by modifying the comparison script in the workflow file
- Negative changes (improvements) are always acceptable

### Example Benchmark Output Interpretation
```
test_large_json_serialization           61,124.9998 (>1000.0)    361,040.9913 (177.27)   82,172.7025 (>1000.0)  27,049.6116 (463.62)   70,666.0212 (>1000.0)  19,238.7670 (inf)         828;754       12.1695 (0.00)       6095           1
```
- **Mean**: 82,172.7025 ns (82 microseconds)
- **OPS**: 12.1695 Kops/s (12,169 operations per second)
- This indicates the test can process about 12,000 large JSON serialization operations per second

### Next Steps
- Developers should run `just benchmark` locally before creating pull requests to establish baselines
- The first successful CI benchmark run will automatically become the baseline for future comparisons
- Performance-critical code changes should include benchmark verification in the development process

### Troubleshooting
**Q: What if there are no baselines?**
A: The workflow will skip comparison and continue with benchmark execution. You can then manually copy the results to `performance-reports/baselines/` for future comparisons.

**Q: How do I update the baseline?**
A: Run `just benchmark` locally, then move the generated JSON file to `performance-reports/baselines/` with a descriptive name like `baseline-<date>.json`.

**Q: Why did my build fail when there shouldn't be performance issues?**
A: Check if the baseline is too old or doesn't match your current code state. Regenerate baselines and ensure they're up to date.

### Performance Regression Detection Algorithm
```python
# Simplified version of the regression detection logic
for benchmark_name, current_metrics in current_results.items():
    if benchmark_name not in baseline_results:
        continue

    for metric in ['time', 'duration']:
        if metric in current_metrics and metric in baseline_metrics:
            percent_change = ((current_value - baseline_value) / baseline_value) * 100
            if percent_change > 5.0:  # Threshold for failure
                regression_detected = True
```

### Workflow File Location
`/.github/workflows/benchmark.yml`

### Baseline Storage Location
`performance-reports/baselines/` (auto-generated by `just benchmark`)

### Current Results Storage Location
`performance-reports/results/` (generated during CI runs)
