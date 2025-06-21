package agentbay_test

import (
	"encoding/json"
	"fmt"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

// Window represents a window in the system (copy of the same struct from window package)
type Window struct {
	WindowID           int      `json:"window_id"`
	Title              string   `json:"title"`
	AbsoluteUpperLeftX int      `json:"absolute_upper_left_x,omitempty"`
	AbsoluteUpperLeftY int      `json:"absolute_upper_left_y,omitempty"`
	Width              int      `json:"width,omitempty"`
	Height             int      `json:"height,omitempty"`
	PID                int      `json:"pid,omitempty"`
	PName              string   `json:"pname,omitempty"`
	ChildWindows       []Window `json:"child_windows,omitempty"`
}

func TestWindow_ListRootWindows(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for window testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test ListRootWindows
	if session.Window != nil {
		fmt.Println("Listing root windows...")
		rootWindows, err := session.Window.ListRootWindows()
		if err != nil {
			t.Logf("Note: ListRootWindows failed: %v", err)
		} else {
			t.Logf("Found %d root windows", len(rootWindows))

			// Verify we got some windows
			if len(rootWindows) == 0 {
				t.Logf("Warning: No root windows found")
			} else {
				// Print the first 3 windows or fewer if less than 3 are available
				count := min(len(rootWindows), 3)
				for i := 0; i < count; i++ {
					t.Logf("Window %d: %s (ID: %d)", i+1, rootWindows[i].Title, rootWindows[i].WindowID)
				}

				// Verify window properties
				for _, window := range rootWindows {
					if window.WindowID <= 0 {
						t.Errorf("Found window with invalid ID: %d", window.WindowID)
					}
				}
			}

			// Check if response contains "tool not found"
			if len(rootWindows) > 0 && testutil.ContainsToolNotFound(rootWindows[0].Title) {
				t.Errorf("Window.ListRootWindows returned 'tool not found'")
			}
		}
	} else {
		t.Logf("Note: Window interface is nil, skipping window test")
	}
}

// extractWindowsFromContent extracts window information from the content field
func extractWindowsFromContent(rawContent interface{}) ([]Window, error) {
	contentArray, ok := rawContent.([]interface{})
	if !ok {
		return nil, fmt.Errorf("content is not an array: %T", rawContent)
	}

	if len(contentArray) == 0 {
		return []Window{}, nil
	}

	// Extract text field from the first content item
	contentItem, ok := contentArray[0].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("content item is not a map: %T", contentArray[0])
	}

	text, ok := contentItem["text"].(string)
	if !ok {
		return nil, fmt.Errorf("text field not found or not a string")
	}

	// Parse the JSON text to get the windows array
	var windows []Window
	if err := json.Unmarshal([]byte(text), &windows); err != nil {
		return nil, fmt.Errorf("failed to unmarshal windows JSON: %w", err)
	}

	return windows, nil
}

func TestWindow_GetActiveWindow(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for active window testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test GetActiveWindow
	if session.Window != nil {
		fmt.Println("Getting active window...")
		activeWindow, err := session.Window.GetActiveWindow()
		if err != nil {
			t.Logf("Note: GetActiveWindow failed: %v", err)
		} else {
			t.Logf("Active window: %s (ID: %d, Process: %s, PID: %d)",
				activeWindow.Title, activeWindow.WindowID, activeWindow.PName, activeWindow.PID)

			// Verify window properties
			if activeWindow.WindowID <= 0 {
				t.Errorf("Active window has invalid ID: %d", activeWindow.WindowID)
			}
			if activeWindow.PID <= 0 {
				t.Errorf("Active window has invalid PID: %d", activeWindow.PID)
			}

			// Check if response contains "tool not found"
			if testutil.ContainsToolNotFound(activeWindow.Title) || testutil.ContainsToolNotFound(activeWindow.PName) {
				t.Errorf("Window.GetActiveWindow returned 'tool not found'")
			}
		}
	} else {
		t.Logf("Note: Window interface is nil, skipping window test")
	}
}

// extractWindowFromContent extracts a single window from the content field
func extractWindowFromContent(rawContent interface{}) (*Window, error) {
	contentArray, ok := rawContent.([]interface{})
	if !ok {
		return nil, fmt.Errorf("content is not an array: %T", rawContent)
	}

	if len(contentArray) == 0 {
		return nil, fmt.Errorf("empty content array")
	}

	// Extract text field from the first content item
	contentItem, ok := contentArray[0].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("content item is not a map: %T", contentArray[0])
	}

	text, ok := contentItem["text"].(string)
	if !ok {
		return nil, fmt.Errorf("text field not found or not a string")
	}

	// Parse the JSON text to get the window
	var window Window
	if err := json.Unmarshal([]byte(text), &window); err != nil {
		return nil, fmt.Errorf("failed to unmarshal window JSON: %w", err)
	}

	return &window, nil
}

func TestWindow_FocusMode(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for focus mode testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		// Make sure to disable focus mode before cleaning up
		if session.Window != nil {
			err := session.Window.FocusMode(false)
			if err != nil {
				t.Logf("Warning: Error disabling focus mode: %v", err)
			}
		}

		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FocusMode
	if session.Window != nil {
		// Enable focus mode
		fmt.Println("Enabling focus mode...")
		err := session.Window.FocusMode(true)
		if err != nil {
			t.Logf("Note: FocusMode(true) failed: %v", err)
		} else {
			t.Log("Focus mode enabled successfully")
		}

		// Wait a short time
		fmt.Println("Waiting briefly...")
		testutil.SleepWithMessage(2, "Focus mode is active...")

		// Disable focus mode
		fmt.Println("Disabling focus mode...")
		err = session.Window.FocusMode(false)
		if err != nil {
			t.Logf("Note: FocusMode(false) failed: %v", err)
		} else {
			t.Log("Focus mode disabled successfully")
		}
	} else {
		t.Logf("Note: Window interface is nil, skipping window test")
	}
}
