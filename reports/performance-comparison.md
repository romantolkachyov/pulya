# Performance Comparison Report

## Overview

This report analyzes performance benchmarks for the Pulya web framework, comparing current implementation against baseline results.

## Key Benchmarks Analyzed

| Benchmark Name | Description |
|---|---|
| `test_static_route_benchmark` | Static route matching performance |
| `test_dynamic_route_benchmark` | Dynamic route matching performance |
| `test_small_json_serialization` | JSON serialization with small payload |
| `test_header_dict_creation` | Header dictionary creation |
| `test_header_list_creation` | Raw header list creation |
| `test_contextvar_set_reset` | Context variable setting/resetting |

## Analysis Methodology

To perform this comparison, the following steps should be executed:

1. **Run Current Benchmarks**:
   ```bash
   uv run pytest benchmarks/ -v --benchmark-json=performance-reports/results/current-$(date +%Y%m%d-%H%M%S).json
   ```

2. **Locate Baseline Files**:
   - Check `performance-reports/baselines/` directory for existing baseline reports
   - If no baseline exists, this run becomes the baseline

3. **Compare Results**:
   - Extract key metrics from both files
   - Calculate percentage changes
   - Identify improvements or regressions

## Expected Performance Characteristics

Based on the code structure and implementation:

### Routing Performance
- Static routes should be very fast with O(1) lookup time
- Dynamic routes with parameter extraction will be slower but still efficient
- The python-matchit library provides high-performance routing

### Serialization Performance
- Small JSON payload serialization should be fast due to msgspec usage
- msgspec is optimized for performance and memory usage

### Header Processing
- Raw header lists creation should be faster than dictionary creation
- Dictionary creation involves additional processing overhead

### Context Management
- Context variable operations are expected to be very fast
- The use of threading.local() (active_request) is designed for minimal overhead

## Recommendations

After running the full benchmark comparison:

1. **If improvements detected**: Keep changes - they show performance enhancements
2. **If regressions detected**: Consider reverting or investigating root cause
3. **If no significant differences**: Maintain current implementation

## Running the Full Analysis

To execute this analysis, run these commands in sequence:

```bash
# Create necessary directories
mkdir -p performance-reports/results
mkdir -p performance-reports/baselines

# Run current benchmarks (this will generate a JSON file)
uv run pytest benchmarks/ -v --benchmark-json=performance-reports/results/current-$(date +%Y%m%d-%H%M%S).json

# Compare with baseline (if available)
# If no baseline exists, move the current result to baseline:
cp performance-reports/results/current-*.json performance-reports/baselines/baseline-$(date +%Y%m%d-%H%M%S).json
```

Once you have both baseline and current results, a detailed comparison can be performed.
