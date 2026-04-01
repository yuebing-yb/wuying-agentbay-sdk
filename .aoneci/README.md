# CI Pipelines

This directory contains CI pipeline configurations for the wuying-agentbay-sdk project.

## Pipeline Overview

| Pipeline | File | Purpose |
|----------|------|---------|
| Example Check | `example-check.yaml` | Validates `ci-stable` marked SDK examples across Python/TypeScript/Golang |
| Integration Test | `smart-integration-test.yaml` | Runs integration tests (supports both blacklist and `ci-stable` whitelist mode) |
| Build & Publish | `test-build-publish.yaml` | Build, test, and publish SDK packages |
| Unit Tests | `unit-tests-only.yml` | Runs unit tests only |
| Pipeline CI | `pipeline-ci.yml` | General CI pipeline |

## CI Testing Strategy

**Core principle: CI only runs examples and tests that can pass reliably.** Unstable, interactive, or environment-dependent cases should be marked to skip.

### When to Skip an Example or Test

Mark a file with `ci-skip` if it falls into any of these categories:

| Category | Description | Example |
|----------|-------------|---------|
| **Interactive** | Requires user input during execution | `call_for_user_jd` |
| **Long-running** | Runs indefinitely or takes >10 minutes | `game_2048`, `game_sudoku` |
| **Unstable external deps** | Depends on 3rd-party services (captchas, etc.) | `captcha_tongcheng` |
| **CI environment limitation** | Requires tools not installed in CI | Golang Playwright driver |
| **Timeout-prone** | Frequently times out in CI (e.g., browser extract) | `network_monitoring` |
| **Connection instability** | Browser/WebSocket connections drop in CI | `browser_dialog_handling` |

### How to Mark a File for CI Skip

Add a `ci-skip` comment in the **first 20 lines** of the file:

**Python:**
```python
# ci-skip: requires interactive user input
```

**TypeScript:**
```typescript
// ci-skip: long running / infinite loop
```

**Golang** (in `main.go`):
```go
// ci-skip: requires local Playwright driver
```

The format is: `<comment-prefix> ci-skip` or `<comment-prefix> ci-skip: <reason>`

The reason is optional but strongly recommended for clarity.

### How It Works

The `scripts/check_examples.py` script scans the first 20 lines of each example file for the `ci-skip` marker before execution. If found, the file is skipped with the reason printed in the CI log.

### Adding a New Example

When adding a new example to the SDK:

1. **Ensure it can run in CI** — no user interaction, completes within 10 minutes, no hard-coded credentials
2. **Use standard image IDs** — `browser_latest`, `mobile_latest`, `linux_latest` (not hard-coded `imgc-*` IDs)
3. **If it cannot run in CI** — add a `ci-skip: <reason>` comment in the first 20 lines
4. **Test locally first** — run `python scripts/check_examples.py --lang <language>` to verify

## CI Stable Tests (`ci-stable`)

In addition to the blacklist approach (`ci-skip`), both integration tests and example code use a **whitelist approach** (`ci-stable`) to ensure a core set always passes in CI.

### How `ci-stable` Works

When `ci_stable` parameter is enabled (default: `true`), the `smart-integration-test.yaml` pipeline **only executes tests and examples marked with `ci-stable`**. This guarantees a stable regression detection baseline that grows over time.

The `ci-stable` marker is used by both:
- `scripts/smart_test_runner.py --ci-stable` for integration tests
- `scripts/check_examples.py --ci-stable` for example code

### How to Mark a Test as CI Stable

Add a `ci-stable` comment in the **first 20 lines** of the test file:

**Python:**
```python
# ci-stable
```

**TypeScript:**
```typescript
// ci-stable
```

**Golang:**
```go
// ci-stable
```

**Java:**
```java
// ci-stable
```

### When to Mark a Test as `ci-stable`

A test should be marked `ci-stable` only if it:

1. **Passes consistently** — verified to pass 3+ times in a row without flakiness
2. **No special environment** — does not require non-default images, endpoints, or tools
3. **Reasonable runtime** — completes within 5 minutes
4. **No external dependencies** — does not depend on 3rd-party services or browser installations

### Expanding the Stable Set

To add more tests to CI stable:

1. Verify the test passes reliably by running it locally 3+ times
2. Add a `ci-stable` comment in the first 20 lines
3. Monitor the next few CI runs to confirm stability
4. If a `ci-stable` test becomes flaky, **remove the marker** and investigate

### Running Locally

```bash
# Run only ci-stable integration tests for all languages
python scripts/smart_test_runner.py --ci-stable --skip-oss

# Run only ci-stable integration tests for a specific language
python scripts/smart_test_runner.py --ci-stable --skip-oss --test-type=python

# Run only ci-stable examples for all languages
python scripts/check_examples.py --ci-stable

# Run only ci-stable examples for a specific language
python scripts/check_examples.py --ci-stable --lang python
```
