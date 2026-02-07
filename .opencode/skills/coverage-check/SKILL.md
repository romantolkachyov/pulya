# Coverage Check Skill

## Overview
This skill provides guidance on handling test coverage requirements, including when to use `# pragma: no cover` comments.

## When 100% Coverage is Impossible

Some code patterns cannot be reasonably tested and should be marked with `# pragma: no cover`:

### 1. Import Fallback Exception Handlers
```python
try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:  # pragma: no cover
    ORJSON_AVAILABLE = False
```

**Why**: Import failures cannot be easily simulated in tests without breaking the test environment.

### 2. `if __name__ == "__main__"` Blocks
```python
if __name__ == "__main__":  # pragma: no cover
    main()
```

**Why**: These blocks are only executed when running the file directly, not when imported as a module.

### 3. `if TYPE_CHECKING` Blocks
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any
```

**Why**: These blocks are only evaluated by type checkers, never at runtime.

### 4. Platform-Specific Code
```python
if sys.platform == "win32":  # pragma: no cover
    # Windows-specific code
    pass
```

**Why**: Cannot test platform-specific code on different platforms.

### 5. Debug/Development Only Code
```python
if DEBUG_MODE:  # pragma: no cover
    print("Debug info")
```

**Why**: Debug code paths are not part of normal production execution.

## Guidelines for Using `# pragma: no cover`

1. **Document the reason**: Add a comment explaining why the code is unreachable
2. **Use sparingly**: Only for legitimately unreachable code, not lazy testing
3. **Review carefully**: Ensure the code truly cannot be tested
4. **Escalate if uncertain**: When in doubt, escalate to lead for decision

## Escalation Criteria

Escalate to lead when:
- Uncertain if code should be marked with `# pragma: no cover`
- Coverage gap is >5% of total codebase
- The uncovered code contains business logic (not just infrastructure)
- Multiple files require pragma comments

## Decision Tree

```
Is the code unreachable in normal execution?
├── Yes → Can it be tested with reasonable effort?
│   ├── Yes → Write tests
│   └── No → Use `# pragma: no cover` with documentation
└── No → Write tests to cover it
```

## Examples of GOOD Usage

```python
# Import fallbacks - cannot test without breaking imports
try:
    import fast_optional_dep
    HAS_FAST_DEP = True
except ImportError:  # pragma: no cover
    HAS_FAST_DEP = False

# Platform specific
try:
    import termios
except ImportError:  # pragma: no cover  # Windows doesn't have termios
    termios = None

# Runtime version checks
if sys.version_info < (3, 10):  # pragma: no cover
    # Backward compatibility code for old Python versions
    pass
```

## Examples of BAD Usage

```python
# Don't use pragma to avoid testing business logic
def calculate_price(amount):  # pragma: no cover  # BAD!
    return amount * 1.2

# Don't use pragma for error handling that should be tested
try:
    risky_operation()
except ValueError:  # pragma: no cover  # BAD - should test this!
    handle_error()
```

## Verification

After adding `# pragma: no cover`:

```bash
# Run coverage check
uv run pytest --cov=pulya --cov-fail-under=100

# Review pragma usage
grep -r "pragma: no cover" src/

# Ensure no business logic is marked
```

## Related

- Project requirement: 100% test coverage
- Exception: Legitimately unreachable code paths
- Tool: pytest-cov with coverage reporting
