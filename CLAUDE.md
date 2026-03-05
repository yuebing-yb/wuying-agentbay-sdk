# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentBay SDK is a multi-language SDK for interacting with Alibaba Cloud's AgentBay cloud runtime environment. It provides capabilities for:
- **Browser Use**: Web automation, scraping, form filling via Playwright/CDP
- **Computer Use**: Windows/Linux desktop automation
- **Mobile Use**: Android mobile UI automation
- **CodeSpace**: Code execution in cloud environments

## Multi-Language Structure

The SDK is implemented in 4 languages with parallel structure:

```
├── python/           # Python SDK (Poetry-based)
├── typescript/       # TypeScript SDK (npm/Node.js)
├── golang/           # Go SDK
└── java/             # Java SDK
```

Each language SDK has:
- Sync API (default, e.g., `python/agentbay/_sync/`)
- Async API (explicit, e.g., `python/agentbay/_async/`)
- Shared components (e.g., `python/agentbay/_common/`)

## Build & Development Commands

### Python
```bash
# Install dependencies
cd python && poetry install

# Run tests
poetry run pytest
poetry run pytest tests/unit -v  # Unit tests only
poetry run pytest tests/integration -v  # Integration tests

# Lint and format
poetry run black .
poetry run flake8 .
poetry run mypy .

# Build package
poetry build
```

### TypeScript
```bash
# Install dependencies
cd typescript && npm install

# Run tests
npm test
npm run test:unit
npm run test:integration
npm run test:coverage

# Lint and format
npm run lint
npm run format

# Build package
npm run build
```

### Golang
```bash
# Install dependencies
cd golang && go mod download

# Run tests
go test ./...
go test ./pkg/agentbay/... -v

# Generate API docs
go run scripts/generate_api_docs.go
```

### Running Examples
```bash
# Set API key first
export AGENTBAY_API_KEY=your_api_key_here

# Python example
python python/docs/examples/_sync/common-features/basics/session_creation/main.py

# TypeScript example
cd typescript && node docs/examples/common-features/basics/session-creation/main.js

# Go example
cd golang/docs/examples/common-features/basics/session_creation && go run main.go
```

## Architecture Patterns

### Core Session Pattern
All SDKs follow the same session-based workflow:
1. Create `AgentBay` client with API key
2. Create session via `client.create(params)` → returns `Session`
3. Use session modules: `session.command`, `session.browser`, `session.code`, etc.
4. Clean up via `client.delete(session)`

### Module Structure per Session
Each `Session` exposes these modules:
- `command` - Execute shell commands
- `filesystem` - File operations (read, write, upload, download)
- `code` - Run Python/JavaScript code
- `browser` - Browser automation (Playwright CDP)
- `computer` - Desktop GUI automation
- `mobile` - Mobile device automation
- `context` - Persistent data storage across sessions
- `oss` - Object Storage Service integration

### Context Synchronization
Data persistence uses `Context` + `ContextSync`:
- `Context` - Persistent storage that survives session deletion
- `ContextSync` - Configures sync policies between session and context
- Sync policies control upload/download strategies, file filters, lifecycle

### Browser Integration
Browser automation uses CDP (Chrome DevTools Protocol):
1. Initialize browser: `session.browser.initialize(BrowserOption)`
2. Get endpoint: `session.browser.get_endpoint_url()`
3. Connect Playwright: `playwright.chromium.connect_over_cdp(endpoint)`

## Key Configuration

### Environment Variables
```bash
AGENTBAY_API_KEY=your_api_key       # Required
DASHSCOPE_API_KEY=xxx               # For AI agent features (optional)
```

### Session Image Types
- `code_latest` - Code execution environment
- `browser_latest` - Browser automation environment
- `windows_latest` / `linux_latest` - Desktop automation
- `mobile_latest` - Android mobile automation

## Documentation Generation

- Python: Docstrings in code, README files in `python/docs/`
- TypeScript: Typedoc, generated in `typescript/docs/api/`
- Golang: Godoc, run `go run scripts/generate_api_docs.go`
- All docs are aggregated in `docs/` and `llms-full.txt`

## Testing Guidelines

- Unit tests: Mock API calls, test local logic
- Integration tests: Require `AGENTBAY_API_KEY`, create real sessions
- Test examples: `scripts/verify_doc_examples.py` validates runnable examples
- Use `scripts/smart_test_runner.py` for intelligent test selection

## Common Pitfalls

1. **API Key Missing**: Always check `AGENTBAY_API_KEY` is set before examples
2. **Session Cleanup**: Sessions cost resources; always delete after use
3. **Resource Creation Delay**: New accounts may see 90s delay for first session
4. **Sync/Async Confusion**: Python has both sync (`_sync/`) and async (`_async/`) APIs
5. **Browser Context**: Use `browser_context=BrowserContext()` when initializing browser to persist state

## Scripts & Tooling

- `scripts/build_llms_txt.py` - Generates documentation aggregation
- `scripts/check_markdown.py` - Validates markdown links
- `scripts/verify_doc_examples.py` - Ensures example code is runnable
- `scripts/sync-aliyun-to-remotes.sh` - Sync code between internal/external repos
