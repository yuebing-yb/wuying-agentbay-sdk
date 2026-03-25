# CI Pipelines

This directory contains CI pipeline configurations for the wuying-agentbay-sdk project.

## Pipeline Overview

| Pipeline | File | Purpose |
|----------|------|---------|
| Example Check | `example-check.yaml` | Validates all SDK example code across Python/TypeScript/Golang |
| Integration Test | `smart-integration-test.yaml` | Runs integration tests against real backend |
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

Add a `ci-skip` comment in the **first 10 lines** of the file:

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

The `scripts/check_examples.py` script scans the first 10 lines of each example file for the `ci-skip` marker before execution. If found, the file is skipped with the reason printed in the CI log.

### Adding a New Example

When adding a new example to the SDK:

1. **Ensure it can run in CI** — no user interaction, completes within 10 minutes, no hard-coded credentials
2. **Use standard image IDs** — `browser_latest`, `mobile_latest`, `linux_latest` (not hard-coded `imgc-*` IDs)
3. **If it cannot run in CI** — add a `ci-skip: <reason>` comment in the first 10 lines
4. **Test locally first** — run `python scripts/check_examples.py --lang <language>` to verify
