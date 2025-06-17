package ui_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/ui"
)

func TestKeyCodeConstants(t *testing.T) {
	// Test that KeyCode constants are defined correctly
	if ui.KeyCode.HOME != 3 {
		t.Errorf("Expected KeyCode.HOME to be 3, got %d", ui.KeyCode.HOME)
	}
	if ui.KeyCode.BACK != 4 {
		t.Errorf("Expected KeyCode.BACK to be 4, got %d", ui.KeyCode.BACK)
	}
	if ui.KeyCode.VOLUME_UP != 24 {
		t.Errorf("Expected KeyCode.VOLUME_UP to be 24, got %d", ui.KeyCode.VOLUME_UP)
	}
	if ui.KeyCode.VOLUME_DOWN != 25 {
		t.Errorf("Expected KeyCode.VOLUME_DOWN to be 25, got %d", ui.KeyCode.VOLUME_DOWN)
	}
	if ui.KeyCode.POWER != 26 {
		t.Errorf("Expected KeyCode.POWER to be 26, got %d", ui.KeyCode.POWER)
	}
	if ui.KeyCode.MENU != 82 {
		t.Errorf("Expected KeyCode.MENU to be 82, got %d", ui.KeyCode.MENU)
	}
}
