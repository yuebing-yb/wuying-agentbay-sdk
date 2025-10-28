package agentbay

import (
	"regexp"
	"runtime/debug"
	"strings"
)

// Version is the current version of the AgentBay SDK
// This can be overridden at build time using:
//
//	go build -ldflags "-X github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay.Version=x.y.z"
//
// If not overridden, it will try to read from Go module info, or fallback to default
var Version = getVersion()

// IsRelease indicates whether this is a release build
// A release build is identified by a git tag matching "golang/v*" pattern
// This can also be overridden at build time using:
//
//	go build -ldflags "-X github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay.IsRelease=true"
var IsRelease = "false"

// getVersion attempts to read version from Go module info
// Returns the version from go.mod or a default fallback
func getVersion() string {
	// Try to read from build info (available in Go 1.18+)
	if info, ok := debug.ReadBuildInfo(); ok {
		// Look for this module's version
		for _, dep := range info.Deps {
			if dep.Path == "github.com/aliyun/wuying-agentbay-sdk/golang" {
				if dep.Version != "" && dep.Version != "(devel)" {
					return dep.Version
				}
			}
		}

		// Check main module version
		if info.Main.Version != "" && info.Main.Version != "(devel)" {
			return info.Main.Version
		}
	}

	// Fallback to default version
	return "0.9.0"
}

// isReleaseVersion checks if the version string indicates a release build
// Returns true if:
// 1. IsRelease is explicitly set to "true" (via -ldflags)
// 2. Version matches the pattern "golang/v*" (e.g., "golang/v0.9.0")
// 3. Version is a semantic version tag (e.g., "v0.9.0")
func isReleaseVersion() bool {
	// Check if explicitly set via -ldflags
	if strings.ToLower(IsRelease) == "true" {
		return true
	}

	// Check if version matches golang release tag pattern (golang/v*)
	if matched, _ := regexp.MatchString(`^golang/v\d+\.\d+\.\d+`, Version); matched {
		return true
	}

	// Check if version is a semantic version tag (v*.*.*)
	// This covers versions from go.mod like "v0.9.0"
	if matched, _ := regexp.MatchString(`^v\d+\.\d+\.\d+`, Version); matched {
		return true
	}

	return false
}
