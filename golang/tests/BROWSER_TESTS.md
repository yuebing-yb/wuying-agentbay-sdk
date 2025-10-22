# Browser Tests for Golang SDK

This document describes the test cases created for the Golang browser module in the wuying-agentbay-sdk.

## Test Structure

The browser tests are organized into three categories:

### 1. Unit Tests (`tests/pkg/unit/browser_test.go`)

Unit tests that test individual browser components in isolation without requiring external dependencies.

**Test Cases:**
- `TestBrowserOption_NewBrowserOption` - Tests default browser option initialization
- `TestBrowserOption_Validate` - Tests validation of browser options including:
  - Valid browser types (chrome, chromium)
  - Invalid browser types (firefox, etc.)
  - Proxy configuration validation
  - Extension path validation
- `TestBrowserOption_ToMap` - Tests conversion of browser options to map format
- `TestBrowserProxy_NewBrowserProxy` - Tests proxy creation with validation:
  - Custom proxies with server configuration
  - Wuying proxies with restricted/polling strategies
  - Invalid proxy configurations
- `TestBrowserFingerprint_NewBrowserFingerprint` - Tests fingerprint configuration:
  - Valid devices (desktop, mobile)
  - Valid operating systems (windows, macos, linux, android, ios)
  - Invalid configurations
- `TestBrowser_IsInitialized` - Tests browser initialization state
- `TestBrowser_GetOption` - Tests retrieval of browser options

**Running Unit Tests:**
```bash
cd golang/tests/pkg/unit
go test -v -run TestBrowser
```

### 2. Integration Tests (`tests/pkg/integration/browser_integration_test.go`)

Integration tests that require a live AgentBay API connection and test the full browser initialization flow.

**Test Cases:**
- `TestBrowser_Initialize_Integration` - Tests basic browser initialization with default options
- `TestBrowser_InitializeWithChrome_Integration` - Tests Chrome browser type selection (requires computer_use_latest image)
- `TestBrowser_InitializeWithCustomOptions_Integration` - Tests initialization with custom viewport, user agent, etc.
- `TestBrowser_InitializeAlreadyInitialized_Integration` - Tests behavior when initializing an already initialized browser
- `TestBrowser_GetEndpointURLBeforeInitialization_Integration` - Tests error handling when getting endpoint URL before initialization
- `TestBrowser_VPCMode_Integration` - Tests browser initialization in VPC mode

**Requirements:**
- `AGENTBAY_API_KEY` environment variable must be set
- Active AgentBay account with available sessions
- For VPC tests: `AGENTBAY_VPC_ENABLED=true` environment variable

**Running Integration Tests:**
```bash
cd golang/tests/pkg/integration
export AGENTBAY_API_KEY=your_api_key
go test -v -run TestBrowser -timeout 5m
```

### 3. Module Tests (`tests/pkg/agentbay/browser_test.go`)

Tests that verify browser integration with the Session module and comprehensive option testing.

**Test Cases:**
- `TestSession_BrowserIntegration` - Tests browser initialization in session context
- `TestBrowserOption_BrowserType` - Tests all browser type values
- `TestBrowserOption_ToMapWithBrowserType` - Tests option serialization with browser types
- `TestBrowserProxy_ToMap` - Tests proxy configuration serialization
- `TestBrowserFingerprint_ToMap` - Tests fingerprint configuration serialization
- `TestBrowserViewportAndScreen_ToMap` - Tests viewport and screen configuration serialization
- `TestBrowserOption_WithProxies` - Tests browser options with proxy configurations

**Running Module Tests:**
```bash
cd golang/tests/pkg/agentbay
go test -v -run TestBrowser
go test -v -run TestSession_BrowserIntegration
```

## Key Features Tested

### 1. Browser Type Selection
The tests verify that users can choose between Chrome and Chromium browsers:
```go
option := browser.NewBrowserOption()
option.BrowserType = "chrome"  // or "chromium"
```

### 2. Browser Options
Tests cover all browser configuration options:
- `UseStealth` - Stealth mode
- `UserAgent` - Custom user agent
- `Viewport` - Browser viewport dimensions
- `Screen` - Screen dimensions
- `BrowserType` - Chrome or Chromium
- `SolveCaptchas` - Automatic captcha solving
- `ExtensionPath` - Browser extensions
- `Proxies` - Proxy configuration
- `Fingerprint` - Browser fingerprinting

### 3. Proxy Configuration
Tests validate both custom and wuying proxy types:
- Custom proxies with server/username/password
- Wuying proxies with restricted or polling strategies

### 4. Fingerprint Configuration
Tests verify device and OS fingerprinting:
- Device types: desktop, mobile
- Operating systems: windows, macos, linux, android, ios
- Locales: en-US, zh-CN, etc.

### 5. Error Handling
Tests ensure proper error handling for:
- Invalid browser types
- Uninitialized browser access
- Invalid proxy configurations
- Empty extension paths
- Multiple proxy configurations

## Test Coverage

The test suite provides comprehensive coverage of:
- ✅ Browser option creation and validation
- ✅ Browser initialization (with and without custom options)
- ✅ Browser type selection (Chrome vs Chromium)
- ✅ Proxy configuration (custom and wuying proxies)
- ✅ Fingerprint configuration
- ✅ Viewport and screen configuration
- ✅ Session integration
- ✅ VPC mode support
- ✅ Error scenarios and edge cases

## Running All Browser Tests

To run all browser tests together:

```bash
# From the golang directory
go test ./tests/pkg/unit ./tests/pkg/agentbay -v -run TestBrowser

# With integration tests (requires API key)
export AGENTBAY_API_KEY=your_api_key
go test ./tests/... -v -run TestBrowser -timeout 10m
```

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Unit tests (no external dependencies)
- name: Run Unit Tests
  run: |
    cd golang/tests/pkg/unit
    go test -v -run TestBrowser

# Integration tests (requires API key)
- name: Run Integration Tests
  env:
    AGENTBAY_API_KEY: ${{ secrets.AGENTBAY_API_KEY }}
  run: |
    cd golang/tests/pkg/integration
    go test -v -run TestBrowser -timeout 5m
```

## Test Maintenance

When adding new browser features:
1. Add unit tests for the new feature in `unit/browser_test.go`
2. Add integration tests if the feature requires API interaction
3. Update existing tests if the feature affects browser initialization
4. Update this documentation with new test cases

## References

- TypeScript tests: `/typescript/tests/integration/browser-*.test.ts`
- TypeScript unit tests: `/typescript/tests/unit/browser-*.test.ts`
- Browser implementation: `/golang/pkg/agentbay/browser/browser.go`
- Session integration: `/golang/pkg/agentbay/session.go`

