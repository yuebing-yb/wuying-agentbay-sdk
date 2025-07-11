package agentbay

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Config stores SDK configuration
type Config struct {
	RegionID  string `json:"region_id"`
	Endpoint  string `json:"endpoint"`
	TimeoutMs int    `json:"timeout_ms"`
}

// DefaultConfig returns the default configuration
func DefaultConfig() Config {
	return Config{
		RegionID:  "cn-shanghai",
		Endpoint:  "wuyingai.cn-shanghai.aliyuncs.com",
		TimeoutMs: 300000,
	}
}

// LoadConfig loads the configuration from file
func LoadConfig() Config {
	// First check if the config file path is specified in environment variables
	configPath := os.Getenv("AGENTBAY_CONFIG_PATH")
	if configPath == "" {
		// Try to find the config file by traversing up from the current directory
		dir, err := os.Getwd()
		if err != nil {
			fmt.Printf("Warning: Failed to get current working directory: %v, using default values\n", err)
			return DefaultConfig()
		}

		// Start from current directory and traverse up to find .config.json
		// This will check current dir, parent, grandparent, etc. up to filesystem root
		found := false
		for i := 0; i < 10; i++ { // Limit search depth to prevent infinite loop
			possibleConfigPath := filepath.Join(dir, ".config.json")
			if _, err := os.Stat(possibleConfigPath); err == nil {
				configPath = possibleConfigPath
				found = true
				fmt.Printf("Found config file at: %s\n", possibleConfigPath)
				break
			}

			// Move up one directory
			parentDir := filepath.Dir(dir)
			if parentDir == dir {
				// We've reached the filesystem root
				break
			}
			dir = parentDir
		}

		if !found {
			fmt.Println("Warning: Configuration file not found, using default values")
			return DefaultConfig()
		}
	}

	// Read the config file
	data, err := os.ReadFile(configPath)
	if err != nil {
		fmt.Printf("Warning: Failed to read configuration file: %v, using default values\n", err)
		return DefaultConfig()
	}

	// Parse JSON
	var config Config
	if err := json.Unmarshal(data, &config); err != nil {
		fmt.Printf("Warning: Failed to parse configuration file: %v, using default values\n", err)
		return DefaultConfig()
	}

	// Allow environment variables to override config file values
	if regionID := os.Getenv("AGENTBAY_REGION_ID"); regionID != "" {
		config.RegionID = regionID
	}
	if endpoint := os.Getenv("AGENTBAY_ENDPOINT"); endpoint != "" {
		config.Endpoint = endpoint
	}

	return config
}
