package agentbay

import (
	// "encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/joho/godotenv"
)

// Config stores SDK configuration
type Config struct {
	Endpoint  string `json:"endpoint"`
	TimeoutMs int    `json:"timeout_ms"`
	RegionID  string `json:"region_id"`
}

// defaultConfig returns the default configuration
func defaultConfig() Config {
	return Config{
		Endpoint:  "wuyingai.cn-shanghai.aliyuncs.com",
		TimeoutMs: 60000,
		RegionID:  "",
	}
}

// findDotEnvFile searches for .env file upward from startPath.
// Search order:
// 1. Current working directory
// 2. Parent directories (up to root)
// 3. Git repository root (if found)
//
// Args:
//
//	startPath: Starting directory for search (empty string means current directory)
//
// Returns:
//
//	Path to .env file if found, empty string otherwise
func findDotEnvFile(startPath string) string {
	if startPath == "" {
		workingDir, err := os.Getwd()
		if err != nil {
			fmt.Printf("Warning: Failed to get current working directory: %v\n", err)
			return ""
		}
		startPath = workingDir
	}

	currentPath, err := filepath.Abs(startPath)
	if err != nil {
		fmt.Printf("Warning: Failed to resolve absolute path: %v\n", err)
		return ""
	}

	// Search upward until we reach root directory
	for {
		envFile := filepath.Join(currentPath, ".env")
		if _, err := os.Stat(envFile); err == nil {
			fmt.Printf("Found .env file at: %s\n", envFile)
			return envFile
		}

		// Check if this is a git repository root
		gitDir := filepath.Join(currentPath, ".git")
		if _, err := os.Stat(gitDir); err == nil {
			fmt.Printf("Found git repository root at: %s\n", currentPath)
		}

		parentPath := filepath.Dir(currentPath)
		if parentPath == currentPath {
			// Reached root directory
			break
		}
		currentPath = parentPath
	}

	return ""
}

// loadDotEnvWithFallback loads .env file with improved search strategy.
//
// Args:
//
//	customEnvPath: Custom path to .env file (empty string means search upward)
func loadDotEnvWithFallback(customEnvPath string) {
	if customEnvPath != "" {
		// Use custom path if provided
		if _, err := os.Stat(customEnvPath); err == nil {
			err = godotenv.Load(customEnvPath)
			if err != nil {
				fmt.Printf("Warning: Failed to load custom .env file %s: %v\n", customEnvPath, err)
			} else {
				fmt.Printf("Loaded custom .env file from: %s\n", customEnvPath)
				return
			}
		} else {
			fmt.Printf("Warning: Custom .env file not found: %s\n", customEnvPath)
		}
	}

	// Find .env file using upward search
	envFile := findDotEnvFile("")
	if envFile != "" {
		err := godotenv.Load(envFile)
		if err != nil {
			fmt.Printf("Warning: Failed to load .env file %s: %v\n", envFile, err)
		} else {
			fmt.Printf("Loaded .env file from: %s\n", envFile)
		}
	} else {
		fmt.Printf("No .env file found in current directory or parent directories\n")
	}
}

// loadConfig loads the configuration from file or environment variables.
// The SDK uses the following precedence order for configuration (highest to lowest):
// 1. Explicitly passed configuration in code.
// 2. Environment variables.
// 3. .env file (searched upward from current directory).
// 4. Default configuration.
//
// Args:
//
//	cfg: Configuration object (if provided, skips env loading)
//	customEnvPath: Custom path to .env file (empty string means search upward)
func loadConfig(cfg *Config, customEnvPath string) Config {
	if cfg != nil {
		// If config is explicitly provided, do NOT load env/.env.
		// Fill missing/zero fields with defaults, but preserve explicit values.
		config := defaultConfig()
		if cfg.Endpoint != "" {
			config.Endpoint = cfg.Endpoint
		}
		if cfg.TimeoutMs > 0 {
			config.TimeoutMs = cfg.TimeoutMs
		}
		if cfg.RegionID != "" {
			config.RegionID = cfg.RegionID
		}
		return config
	}

	// Load .env file with improved search
	loadDotEnvWithFallback(customEnvPath)

	// Use environment variables if set (highest priority)
	config := defaultConfig()

	if endpoint := os.Getenv("AGENTBAY_ENDPOINT"); endpoint != "" {
		config.Endpoint = endpoint
	}
	if timeoutMS := os.Getenv("AGENTBAY_TIMEOUT_MS"); timeoutMS != "" {
		_, err := fmt.Sscanf(timeoutMS, "%d", &config.TimeoutMs)
		if err != nil {
			// Warning: Failed to parse AGENTBAY_TIMEOUT_MS as integer, using default
		}
	}
	if regionID := os.Getenv("AGENTBAY_REGION_ID"); regionID != "" {
		config.RegionID = regionID
	}

	return config
}

// loadConfigCompat provides backward compatibility for existing code
func loadConfigCompat(cfg *Config) Config {
	return loadConfig(cfg, "")
}

// BrowserRecordPath is the path constant for browser recording data.
// This path is used when syncing browser recording context during session deletion.
const BrowserRecordPath = "/home/wuying/record"

// MobileInfoDefaultPath is path constant for internal create context
const MobileInfoDefaultPath = "/data/agentbay_mobile_info"

// MobileInfoSubPath is mobile dev info sub path constant when append to user's context path
const MobileInfoSubPath = "/agentbay_mobile_info/"

// MobileInfoFileName is mobile dev info file name constant
const MobileInfoFileName = "dev_info.json"

// configManager implementation for backward compatibility
type configManager struct{}

// loadConfig implements the ConfigInterface for backward compatibility
func (c *configManager) loadConfig(cfg *Config) Config {
	return loadConfigCompat(cfg)
}

// defaultConfig implements the ConfigInterface
func (c *configManager) defaultConfig() Config {
	return defaultConfig()
}

// newConfigManager creates a new configManager instance
func newConfigManager() *configManager {
	return &configManager{}
}
