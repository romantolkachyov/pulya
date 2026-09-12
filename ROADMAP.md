# Pulya Framework Performance Roadmap

## 1. Guiding Principles
- **Measure first, optimize second**: All performance changes must be benchmarked before and after implementation to ensure measurable improvements.
- **Backward compatibility**: All optimizations must maintain full backward compatibility with existing applications.
- **Testing requirements**: Maintain 100% test coverage for all changes. Add benchmarks as tests where applicable.
- **Documentation requirements**: Document the rationale, expected gains, and usage instructions for each optimization.

## 2. Current Status

### Phase 0 - Foundation ✅ COMPLETE
- Benchmark suite established
- Profiling tools added
- CI workflow for performance regression detection
- Baseline metrics established

### Phase 1 - Quick Wins ✅ COMPLETE
- 1.1 Pre-encoded 404 response body (the hottest error path)
- 1.2 __slots__ optimization (memory optimization)
- 1.3 ~~LRU cache for route matching~~ ❌ REVERTED (routing is delegated to python-matchit — a Rust matcher; an extra cache adds overhead without gains)

### Phase 2 - Core Optimizations ✅ COMPLETE
- 2.1 Route Trie - ATTEMPTED BUT REVERTED (caused slowdown; the matchit-only approach is optimal)
- 2.2 ~~Optional orjson encoder support~~ ❌ (removed - does not support free-threaded Python)
- 2.3 ~~Replace threading.Lock with asyncio.Lock~~ ❌ NOT ADOPTED (`threading.Lock` is only taken in `on_startup`/`on_shutdown`, not on the request path; an `asyncio.Lock` buys nothing there)

### Phase 3 - Advanced Optimizations 🔄 IN PROGRESS
- 3.1 Header dictionary optimization ⏳ PENDING (experimental changes exist, not merged)
- 3.2 ~~Request/Scope object pooling~~ ❌ REMOVED (Request objects are bound to their scope/protocol and cannot be reset safely; pooling infrastructure was dead code)
- 3.3 Pre-compile routes and cache schemas at startup ⏳ PENDING

### Phase 4 - Continuous ⏳ PENDING
- 4.0 Performance monitoring setup

## 3. Future Work (Backlog)

### Phase 3.3 - Pre-compile routes and cache schemas at startup
- Implement pre-compilation of all route patterns during application startup in `routing.py`
- Cache msgspec schemas for frequently used models
- Pre-allocate common objects to reduce runtime overhead

### Phase 4 - Continuous Optimization
- Set up continuous benchmarking in CI/CD pipeline
- Implement performance regression detection with automated alerts
- Monitor key metrics (latency, throughput, memory usage)
- Collect user performance reports and real-world bottlenecks
- Prioritize optimizations based on actual usage patterns

## 4. Current Metrics
- All tests pass with 100% coverage, 0 ruff errors, 0 mypy errors
- Benchmarks run with stabilized methodology (fixed iterations/rounds, GC disabled during timing, PYTHONHASHSEED=0); run `just benchmark-compare` for up-to-date numbers
