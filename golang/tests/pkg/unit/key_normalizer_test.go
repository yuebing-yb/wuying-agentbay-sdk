package unit

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/assert"
)

// TestNormalizeSingleKey_LetterKeys tests normalization of letter keys
func TestNormalizeSingleKey_LetterKeys(t *testing.T) {
	assert.Equal(t, "a", agentbay.NormalizeSingleKey("a"), "Lowercase letter should remain lowercase")
	assert.Equal(t, "a", agentbay.NormalizeSingleKey("A"), "Uppercase letter should be converted to lowercase")
	assert.Equal(t, "z", agentbay.NormalizeSingleKey("Z"), "Uppercase Z should be converted to lowercase z")
}

// TestNormalizeSingleKey_NumberKeys tests normalization of number keys
func TestNormalizeSingleKey_NumberKeys(t *testing.T) {
	assert.Equal(t, "0", agentbay.NormalizeSingleKey("0"), "Number key should remain as-is")
	assert.Equal(t, "1", agentbay.NormalizeSingleKey("1"), "Number key should remain as-is")
	assert.Equal(t, "9", agentbay.NormalizeSingleKey("9"), "Number key should remain as-is")
}

// TestNormalizeSingleKey_ModifierKeys tests normalization of modifier keys
func TestNormalizeSingleKey_ModifierKeys(t *testing.T) {
	// Ctrl variants
	assert.Equal(t, "Ctrl", agentbay.NormalizeSingleKey("ctrl"), "ctrl should normalize to Ctrl")
	assert.Equal(t, "Ctrl", agentbay.NormalizeSingleKey("CTRL"), "CTRL should normalize to Ctrl")
	assert.Equal(t, "Ctrl", agentbay.NormalizeSingleKey("Ctrl"), "Ctrl should remain Ctrl")
	assert.Equal(t, "Ctrl", agentbay.NormalizeSingleKey("control"), "control should normalize to Ctrl")

	// Alt variants
	assert.Equal(t, "Alt", agentbay.NormalizeSingleKey("alt"), "alt should normalize to Alt")
	assert.Equal(t, "Alt", agentbay.NormalizeSingleKey("ALT"), "ALT should normalize to Alt")
	assert.Equal(t, "Alt", agentbay.NormalizeSingleKey("Alt"), "Alt should remain Alt")

	// Shift variants
	assert.Equal(t, "Shift", agentbay.NormalizeSingleKey("shift"), "shift should normalize to Shift")
	assert.Equal(t, "Shift", agentbay.NormalizeSingleKey("SHIFT"), "SHIFT should normalize to Shift")
	assert.Equal(t, "Shift", agentbay.NormalizeSingleKey("Shift"), "Shift should remain Shift")

	// Win variants
	assert.Equal(t, "Win", agentbay.NormalizeSingleKey("win"), "win should normalize to Win")
	assert.Equal(t, "Win", agentbay.NormalizeSingleKey("WIN"), "WIN should normalize to Win")
	assert.Equal(t, "Win", agentbay.NormalizeSingleKey("windows"), "windows should normalize to Win")
	assert.Equal(t, "Win", agentbay.NormalizeSingleKey("Windows"), "Windows should normalize to Win")

	// Command variants
	assert.Equal(t, "Command", agentbay.NormalizeSingleKey("command"), "command should normalize to Command")
	assert.Equal(t, "Command", agentbay.NormalizeSingleKey("cmd"), "cmd should normalize to Command")

	// Meta/Super
	assert.Equal(t, "Meta", agentbay.NormalizeSingleKey("meta"), "meta should normalize to Meta")
	assert.Equal(t, "Super", agentbay.NormalizeSingleKey("super"), "super should normalize to Super")
}

// TestNormalizeSingleKey_FunctionKeys tests normalization of function keys
func TestNormalizeSingleKey_FunctionKeys(t *testing.T) {
	// Tab
	assert.Equal(t, "Tab", agentbay.NormalizeSingleKey("tab"), "tab should normalize to Tab")
	assert.Equal(t, "Tab", agentbay.NormalizeSingleKey("TAB"), "TAB should normalize to Tab")

	// Enter variants
	assert.Equal(t, "Enter", agentbay.NormalizeSingleKey("enter"), "enter should normalize to Enter")
	assert.Equal(t, "Enter", agentbay.NormalizeSingleKey("ENTER"), "ENTER should normalize to Enter")
	assert.Equal(t, "Enter", agentbay.NormalizeSingleKey("return"), "return should normalize to Enter")

	// Escape variants
	assert.Equal(t, "Escape", agentbay.NormalizeSingleKey("escape"), "escape should normalize to Escape")
	assert.Equal(t, "Escape", agentbay.NormalizeSingleKey("ESC"), "ESC should normalize to Escape")
	assert.Equal(t, "Escape", agentbay.NormalizeSingleKey("esc"), "esc should normalize to Escape")

	// Delete variants
	assert.Equal(t, "Delete", agentbay.NormalizeSingleKey("delete"), "delete should normalize to Delete")
	assert.Equal(t, "Delete", agentbay.NormalizeSingleKey("del"), "del should normalize to Delete")

	// Other function keys
	assert.Equal(t, "Backspace", agentbay.NormalizeSingleKey("backspace"), "backspace should normalize to Backspace")
	assert.Equal(t, "Insert", agentbay.NormalizeSingleKey("insert"), "insert should normalize to Insert")
	assert.Equal(t, "Insert", agentbay.NormalizeSingleKey("ins"), "ins should normalize to Insert")
	assert.Equal(t, "Home", agentbay.NormalizeSingleKey("home"), "home should normalize to Home")
	assert.Equal(t, "End", agentbay.NormalizeSingleKey("end"), "end should normalize to End")
	assert.Equal(t, "PageUp", agentbay.NormalizeSingleKey("pageup"), "pageup should normalize to PageUp")
	assert.Equal(t, "PageDown", agentbay.NormalizeSingleKey("pagedown"), "pagedown should normalize to PageDown")
	assert.Equal(t, "Space", agentbay.NormalizeSingleKey("space"), "space should normalize to Space")
}

// TestNormalizeSingleKey_FKeys tests normalization of F-keys
func TestNormalizeSingleKey_FKeys(t *testing.T) {
	assert.Equal(t, "F1", agentbay.NormalizeSingleKey("f1"), "f1 should normalize to F1")
	assert.Equal(t, "F1", agentbay.NormalizeSingleKey("F1"), "F1 should remain F1")
	assert.Equal(t, "F12", agentbay.NormalizeSingleKey("f12"), "f12 should normalize to F12")
	assert.Equal(t, "F24", agentbay.NormalizeSingleKey("f24"), "f24 should normalize to F24")
}

// TestNormalizeSingleKey_ArrowKeys tests normalization of arrow keys
func TestNormalizeSingleKey_ArrowKeys(t *testing.T) {
	// Full names
	assert.Equal(t, "ArrowUp", agentbay.NormalizeSingleKey("arrowup"), "arrowup should normalize to ArrowUp")
	assert.Equal(t, "ArrowUp", agentbay.NormalizeSingleKey("ARROWUP"), "ARROWUP should normalize to ArrowUp")
	assert.Equal(t, "ArrowDown", agentbay.NormalizeSingleKey("arrowdown"), "arrowdown should normalize to ArrowDown")
	assert.Equal(t, "ArrowLeft", agentbay.NormalizeSingleKey("arrowleft"), "arrowleft should normalize to ArrowLeft")
	assert.Equal(t, "ArrowRight", agentbay.NormalizeSingleKey("arrowright"), "arrowright should normalize to ArrowRight")

	// Short names
	assert.Equal(t, "ArrowUp", agentbay.NormalizeSingleKey("up"), "up should normalize to ArrowUp")
	assert.Equal(t, "ArrowDown", agentbay.NormalizeSingleKey("down"), "down should normalize to ArrowDown")
	assert.Equal(t, "ArrowLeft", agentbay.NormalizeSingleKey("left"), "left should normalize to ArrowLeft")
	assert.Equal(t, "ArrowRight", agentbay.NormalizeSingleKey("right"), "right should normalize to ArrowRight")
}

// TestNormalizeKeys_SingleLetter tests normalization of single letter keys
func TestNormalizeKeys_SingleLetter(t *testing.T) {
	result := agentbay.NormalizeKeys([]string{"a"})
	assert.Equal(t, []string{"a"}, result, "Lowercase letter should remain lowercase")

	result = agentbay.NormalizeKeys([]string{"A"})
	assert.Equal(t, []string{"a"}, result, "Uppercase letter should be converted to lowercase")
}

// TestNormalizeKeys_ModifierCombinations tests normalization of modifier key combinations
func TestNormalizeKeys_ModifierCombinations(t *testing.T) {
	// Ctrl+C (lowercase)
	result := agentbay.NormalizeKeys([]string{"ctrl", "c"})
	assert.Equal(t, []string{"Ctrl", "c"}, result, "ctrl+c should normalize to Ctrl+c")

	// CTRL+C (uppercase)
	result = agentbay.NormalizeKeys([]string{"CTRL", "C"})
	assert.Equal(t, []string{"Ctrl", "c"}, result, "CTRL+C should normalize to Ctrl+c")

	// Ctrl+Shift+Z
	result = agentbay.NormalizeKeys([]string{"ctrl", "shift", "z"})
	assert.Equal(t, []string{"Ctrl", "Shift", "z"}, result, "ctrl+shift+z should normalize correctly")

	// Alt+Tab
	result = agentbay.NormalizeKeys([]string{"alt", "tab"})
	assert.Equal(t, []string{"Alt", "Tab"}, result, "alt+tab should normalize to Alt+Tab")

	// Win+D
	result = agentbay.NormalizeKeys([]string{"win", "d"})
	assert.Equal(t, []string{"Win", "d"}, result, "win+d should normalize to Win+d")
}

// TestNormalizeKeys_MixedCase tests normalization of mixed case combinations
func TestNormalizeKeys_MixedCase(t *testing.T) {
	result := agentbay.NormalizeKeys([]string{"CTRL", "a"})
	assert.Equal(t, []string{"Ctrl", "a"}, result, "CTRL+a should normalize to Ctrl+a")

	result = agentbay.NormalizeKeys([]string{"alt", "TAB"})
	assert.Equal(t, []string{"Alt", "Tab"}, result, "alt+TAB should normalize to Alt+Tab")

	result = agentbay.NormalizeKeys([]string{"ALT", "tab"})
	assert.Equal(t, []string{"Alt", "Tab"}, result, "ALT+tab should normalize to Alt+Tab")
}

// TestNormalizeKeys_FKeysCombinations tests normalization of F-key combinations
func TestNormalizeKeys_FKeysCombinations(t *testing.T) {
	result := agentbay.NormalizeKeys([]string{"alt", "f4"})
	assert.Equal(t, []string{"Alt", "F4"}, result, "alt+f4 should normalize to Alt+F4")

	result = agentbay.NormalizeKeys([]string{"ALT", "F4"})
	assert.Equal(t, []string{"Alt", "F4"}, result, "ALT+F4 should normalize to Alt+F4")
}

// TestNormalizeKeys_ArrowKeysCombinations tests normalization of arrow key combinations
func TestNormalizeKeys_ArrowKeysCombinations(t *testing.T) {
	result := agentbay.NormalizeKeys([]string{"shift", "arrowleft"})
	assert.Equal(t, []string{"Shift", "ArrowLeft"}, result, "shift+arrowleft should normalize correctly")

	result = agentbay.NormalizeKeys([]string{"SHIFT", "LEFT"})
	assert.Equal(t, []string{"Shift", "ArrowLeft"}, result, "SHIFT+LEFT should normalize correctly")
}

// TestNormalizeKeys_Aliases tests normalization of key aliases
func TestNormalizeKeys_Aliases(t *testing.T) {
	// control -> Ctrl
	result := agentbay.NormalizeKeys([]string{"control", "c"})
	assert.Equal(t, []string{"Ctrl", "c"}, result, "control should normalize to Ctrl")

	// windows -> Win
	result = agentbay.NormalizeKeys([]string{"windows", "e"})
	assert.Equal(t, []string{"Win", "e"}, result, "windows should normalize to Win")

	// esc -> Escape
	result = agentbay.NormalizeKeys([]string{"esc"})
	assert.Equal(t, []string{"Escape"}, result, "esc should normalize to Escape")

	// return -> Enter
	result = agentbay.NormalizeKeys([]string{"return"})
	assert.Equal(t, []string{"Enter"}, result, "return should normalize to Enter")

	// del -> Delete
	result = agentbay.NormalizeKeys([]string{"del"})
	assert.Equal(t, []string{"Delete"}, result, "del should normalize to Delete")
}

// TestNormalizeKeys_EmptyInput tests normalization of empty input
func TestNormalizeKeys_EmptyInput(t *testing.T) {
	result := agentbay.NormalizeKeys([]string{})
	assert.Equal(t, []string{}, result, "Empty array should return empty array")

	result = agentbay.NormalizeKeys(nil)
	assert.Nil(t, result, "Nil input should return nil")
}

// TestNormalizeKeys_RealWorldUseCases tests real-world use cases
func TestNormalizeKeys_RealWorldUseCases(t *testing.T) {
	// Copy (Ctrl+C)
	result := agentbay.NormalizeKeys([]string{"ctrl", "c"})
	assert.Equal(t, []string{"Ctrl", "c"}, result, "Copy shortcut should normalize correctly")

	// Paste (Ctrl+V)
	result = agentbay.NormalizeKeys([]string{"CTRL", "V"})
	assert.Equal(t, []string{"Ctrl", "v"}, result, "Paste shortcut should normalize correctly")

	// Undo (Ctrl+Z)
	result = agentbay.NormalizeKeys([]string{"ctrl", "z"})
	assert.Equal(t, []string{"Ctrl", "z"}, result, "Undo shortcut should normalize correctly")

	// Redo (Ctrl+Shift+Z)
	result = agentbay.NormalizeKeys([]string{"ctrl", "shift", "z"})
	assert.Equal(t, []string{"Ctrl", "Shift", "z"}, result, "Redo shortcut should normalize correctly")

	// Alt+Tab (window switching)
	result = agentbay.NormalizeKeys([]string{"alt", "tab"})
	assert.Equal(t, []string{"Alt", "Tab"}, result, "Alt+Tab should normalize correctly")

	// Win+D (show desktop)
	result = agentbay.NormalizeKeys([]string{"win", "d"})
	assert.Equal(t, []string{"Win", "d"}, result, "Win+D should normalize correctly")

	// Alt+F4 (close window)
	result = agentbay.NormalizeKeys([]string{"alt", "f4"})
	assert.Equal(t, []string{"Alt", "F4"}, result, "Alt+F4 should normalize correctly")

	// Shift+ArrowLeft (select text)
	result = agentbay.NormalizeKeys([]string{"shift", "arrowleft"})
	assert.Equal(t, []string{"Shift", "ArrowLeft"}, result, "Shift+ArrowLeft should normalize correctly")
}

// TestGetSupportedKeyNames tests the GetSupportedKeyNames function
func TestGetSupportedKeyNames(t *testing.T) {
	mappings := agentbay.GetSupportedKeyNames()

	// Check that all expected categories exist
	assert.NotNil(t, mappings["modifierKeys"], "modifierKeys should exist")
	assert.NotNil(t, mappings["functionKeys"], "functionKeys should exist")
	assert.NotNil(t, mappings["arrowKeys"], "arrowKeys should exist")
	assert.NotNil(t, mappings["fKeys"], "fKeys should exist")
	assert.NotNil(t, mappings["specialChars"], "specialChars should exist")

	// Check some specific mappings
	assert.Equal(t, "Ctrl", mappings["modifierKeys"]["ctrl"], "ctrl should map to Ctrl")
	assert.Equal(t, "Tab", mappings["functionKeys"]["tab"], "tab should map to Tab")
	assert.Equal(t, "ArrowUp", mappings["arrowKeys"]["up"], "up should map to ArrowUp")
	assert.Equal(t, "F1", mappings["fKeys"]["f1"], "f1 should map to F1")
}
