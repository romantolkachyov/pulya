"""Compare two pytest-benchmark JSON reports, pairing benchmarks by name.

Usage:
    python tools/compare_benchmarks.py BASELINE.json CURRENT.json
"""

# ruff: noqa: T201, PLR2004, INP001
import argparse
import json
from pathlib import Path


def load_benchmarks(path: Path) -> dict[str, dict[str, float]]:
    """Load benchmarks from a pytest-benchmark JSON report, keyed by name."""
    data = json.loads(path.read_text())
    return {
        bench["name"]: bench["stats"]
        for bench in data["benchmarks"]
        if not bench.get("has_error")
    }


def format_time(seconds: float) -> str:
    """Format a duration in seconds as ns/us/ms."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:,.1f} ns"
    if seconds < 1e-3:
        return f"{seconds * 1e6:,.1f} us"
    return f"{seconds * 1e3:,.1f} ms"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path, help="Baseline JSON report")
    parser.add_argument("current", type=Path, help="Current JSON report")
    parser.add_argument(
        "--fail-on-regression",
        type=float,
        metavar="PCT",
        default=None,
        help="Exit with code 1 if any benchmark is more than PCT %% slower",
    )
    args = parser.parse_args()

    baseline = load_benchmarks(args.baseline)
    current = load_benchmarks(args.current)

    rows = []
    for name in sorted(set(baseline) | set(current)):
        base_stats = baseline.get(name)
        curr_stats = current.get(name)
        if base_stats is None or curr_stats is None:
            missing = "baseline" if base_stats is None else "current"
            print(f"WARNING: {name} missing in {missing} report, skipped")
            continue
        base_mean = base_stats["mean"]
        curr_mean = curr_stats["mean"]
        change = (curr_mean - base_mean) / base_mean * 100
        rows.append((name, base_mean, curr_mean, change))

    name_w = max(len(name) for name, *_ in rows)
    print()
    print(
        f"{'Benchmark'.ljust(name_w)}  {'Baseline':>12}  {'Current':>12}  {'Change':>9}"
    )
    print("-" * (name_w + 40))
    for name, base_mean, curr_mean, change in rows:
        verdict = "slower" if change > 1 else "faster" if change < -1 else "~same"
        print(
            f"{name.ljust(name_w)}  {format_time(base_mean):>12}  "
            f"{format_time(curr_mean):>12}  {change:+6.1f}%  {verdict}"
        )
    print()

    if args.fail_on_regression is not None:
        regressions = [
            (name, change)
            for name, _, _, change in rows
            if change > args.fail_on_regression
        ]
        if regressions:
            print(
                f"Performance regressions detected "
                f"(threshold +{args.fail_on_regression:.1f}%):"
            )
            for name, change in regressions:
                print(f"  - {name}: +{change:.1f}% slower")
            raise SystemExit(1)
        print(f"No regressions above +{args.fail_on_regression:.1f}%")


if __name__ == "__main__":
    main()
