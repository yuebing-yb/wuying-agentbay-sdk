#!/bin/bash
# Build Golang SDK with version injection from git tag
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building AgentBay Golang SDK with version injection${NC}"
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Determine version
if git rev-parse --git-dir > /dev/null 2>&1; then
    # We're in a git repository
    if git describe --tags --exact-match > /dev/null 2>&1; then
        # Current commit has a tag
        VERSION=$(git describe --tags --exact-match)
        echo -e "${GREEN}✓${NC} Building release version from tag: ${YELLOW}${VERSION}${NC}"
    else
        # Use tag + commit info
        VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "dev")
        echo -e "${YELLOW}⚠${NC} Building development version: ${YELLOW}${VERSION}${NC}"
    fi
else
    # Not in a git repository, use default
    VERSION="0.14.0"
    echo -e "${YELLOW}⚠${NC} Not in git repository, using default version: ${YELLOW}${VERSION}${NC}"
fi

# Package path for ldflags
PACKAGE_PATH="github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

# Build flags
LDFLAGS="-X ${PACKAGE_PATH}.Version=${VERSION}"

echo ""
echo "Build configuration:"
echo "  Version: ${VERSION}"
echo "  Package: ${PACKAGE_PATH}"
echo "  LDFlags: ${LDFLAGS}"
echo ""

# Run tests first (optional, comment out if not needed)
echo -e "${GREEN}Running tests...${NC}"
if go test ./tests/pkg/unit/... -v > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Tests passed"
else
    echo -e "${RED}✗${NC} Tests failed"
    exit 1
fi

echo ""
echo -e "${GREEN}Building...${NC}"

# Build
if go build -ldflags "${LDFLAGS}" ./...; then
    echo -e "${GREEN}✓${NC} Build successful"
    echo ""
    echo -e "${GREEN}Version injected: ${VERSION}${NC}"
    echo ""
    echo "To verify the version in your code:"
    echo "  import \"${PACKAGE_PATH}\""
    echo "  fmt.Println(agentbay.Version)"
else
    echo -e "${RED}✗${NC} Build failed"
    exit 1
fi

