package agentbay

import (
	"fmt"
	"strings"
)

// Key name normalization utilities for press_keys tool.
//
// This module provides utilities to normalize key names to the correct case format
// expected by the press_keys MCP tool, improving case compatibility.

// Category 1: Modifier keys - should be Title Case
var modifierKeys = map[string]string{
	"ctrl":    "Ctrl",
	"control": "Ctrl",
	"alt":     "Alt",
	"shift":   "Shift",
	"win":     "Win",
	"windows": "Win",
	"meta":    "Meta",
	"super":   "Super",
	"command": "Command",
	"cmd":     "Command",
}

// Category 2: Function keys - should be Title Case
var functionKeys = map[string]string{
	"tab":         "Tab",
	"enter":       "Enter",
	"return":      "Enter",
	"escape":      "Escape",
	"esc":         "Escape",
	"backspace":   "Backspace",
	"delete":      "Delete",
	"del":         "Delete",
	"insert":      "Insert",
	"ins":         "Insert",
	"home":        "Home",
	"end":         "End",
	"pageup":      "PageUp",
	"pagedown":    "PageDown",
	"pgup":        "PageUp",
	"pgdn":        "PageDown",
	"space":       "Space",
	"capslock":    "CapsLock",
	"numlock":     "NumLock",
	"scrolllock":  "ScrollLock",
	"printscreen": "PrintScreen",
	"prtsc":       "PrintScreen",
	"pause":       "Pause",
	"break":       "Pause",
}

// Category 3: Arrow keys - should be Title Case
var arrowKeys = map[string]string{
	"arrowup":    "ArrowUp",
	"arrowdown":  "ArrowDown",
	"arrowleft":  "ArrowLeft",
	"arrowright": "ArrowRight",
	"up":         "ArrowUp",
	"down":       "ArrowDown",
	"left":       "ArrowLeft",
	"right":      "ArrowRight",
}

// Category 4: Special characters - as-is
var specialChars = map[string]string{
	"minus":        "-",
	"equal":        "=",
	"leftbracket":  "[",
	"rightbracket": "]",
	"backslash":    "\\",
	"semicolon":    ";",
	"quote":        "'",
	"comma":        ",",
	"period":       ".",
	"slash":        "/",
	"backtick":     "`",
}

// Category 5: F-keys - Title Case (F1, F2, ..., F24)
var fKeys map[string]string

func init() {
	// Initialize F-keys map
	fKeys = make(map[string]string)
	for i := 1; i <= 24; i++ {
		fKeyLower := fmt.Sprintf("f%d", i)
		fKeyUpper := fmt.Sprintf("F%d", i)
		fKeys[fKeyLower] = fKeyUpper
	}
}

// NormalizeSingleKey normalizes a single key name to the correct case format.
//
// Rules:
//   - Letter keys (a-z): Convert to lowercase
//   - Number keys (0-9): Keep as-is
//   - Modifier keys: Convert to Title Case (Ctrl, Alt, Shift, Win, etc.)
//   - Function keys: Convert to Title Case (Tab, Enter, Escape, etc.)
//   - Arrow keys: Convert to Title Case (ArrowUp, ArrowDown, etc.)
//   - F-keys: Convert to correct format (F1, F2, ..., F12)
//   - Unknown keys: Return as-is
//
// Example:
//
//	NormalizeSingleKey("A")        // returns "a"
//	NormalizeSingleKey("ctrl")     // returns "Ctrl"
//	NormalizeSingleKey("CTRL")     // returns "Ctrl"
//	NormalizeSingleKey("TAB")      // returns "Tab"
//	NormalizeSingleKey("f1")       // returns "F1"
func NormalizeSingleKey(key string) string {
	if key == "" {
		return key
	}

	// Convert to lowercase for comparison
	keyLower := strings.ToLower(key)

	// Check if it's a single letter (a-z)
	if len(key) == 1 && isLetter(key) {
		return strings.ToLower(key)
	}

	// Check if it's a single digit (0-9)
	if len(key) == 1 && isDigit(key) {
		return key
	}

	// Check modifier keys
	if normalized, exists := modifierKeys[keyLower]; exists {
		return normalized
	}

	// Check function keys
	if normalized, exists := functionKeys[keyLower]; exists {
		return normalized
	}

	// Check arrow keys
	if normalized, exists := arrowKeys[keyLower]; exists {
		return normalized
	}

	// Check F-keys
	if normalized, exists := fKeys[keyLower]; exists {
		return normalized
	}

	// Check special characters
	if normalized, exists := specialChars[keyLower]; exists {
		return normalized
	}

	// If the key is already in a known good format (starts with uppercase letter
	// and is not all uppercase), assume it's already correct
	if len(key) > 0 && isUpperCase(key[0]) && key != strings.ToUpper(key) &&
		key != "Control" && key != "Windows" && key != "Command" {
		return key
	}

	// Unknown key - return as-is
	return key
}

// NormalizeKeys normalizes a list of key names to the correct case format for press_keys tool.
//
// This function automatically converts key names to the format expected by the
// press_keys MCP tool, improving case compatibility and user experience.
//
// Example:
//
//	NormalizeKeys([]string{"CTRL", "C"})           // returns ["Ctrl", "c"]
//	NormalizeKeys([]string{"ctrl", "shift", "Z"})  // returns ["Ctrl", "Shift", "z"]
//	NormalizeKeys([]string{"alt", "TAB"})          // returns ["Alt", "Tab"]
//	NormalizeKeys([]string{"win", "d"})            // returns ["Win", "d"]
//
// Note:
//   - Modifier keys are converted to Title Case (Ctrl, Alt, Shift, Win)
//   - Function keys are converted to Title Case (Tab, Enter, Escape)
//   - Letter keys are converted to lowercase (a, b, c)
//   - Number keys remain unchanged (0, 1, 2)
//   - Unknown keys are returned as-is
func NormalizeKeys(keys []string) []string {
	if keys == nil {
		return keys
	}

	normalized := make([]string, 0, len(keys))
	for _, key := range keys {
		normalized = append(normalized, NormalizeSingleKey(key))
	}

	return normalized
}

// Helper functions
func isLetter(s string) bool {
	if len(s) != 1 {
		return false
	}
	c := s[0]
	return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
}

func isDigit(s string) bool {
	if len(s) != 1 {
		return false
	}
	c := s[0]
	return c >= '0' && c <= '9'
}

func isUpperCase(c byte) bool {
	return c >= 'A' && c <= 'Z'
}

// GetSupportedKeyNames returns a dictionary of all supported key name mappings.
//
// Returns:
//
//	A map with categories and their supported key names
//
// Example:
//
//	mappings := GetSupportedKeyNames()
//	fmt.Println(mappings["modifierKeys"])  // map[ctrl:Ctrl alt:Alt ...]
func GetSupportedKeyNames() map[string]map[string]string {
	return map[string]map[string]string{
		"modifierKeys": modifierKeys,
		"functionKeys": functionKeys,
		"arrowKeys":    arrowKeys,
		"fKeys":        fKeys,
		"specialChars": specialChars,
	}
}
