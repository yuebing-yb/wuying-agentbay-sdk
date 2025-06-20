package integration_test

import (
	"encoding/json"
	"fmt"
	"sort"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/application"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

// extractProcesses parses a JSON string into a slice of Process objects
func extractProcesses(textContent string) ([]application.Process, error) {
	if textContent == "" {
		return nil, fmt.Errorf("empty content string")
	}

	// Parse the JSON text into Process objects
	var processes []application.Process
	if err := json.Unmarshal([]byte(textContent), &processes); err != nil {
		return nil, fmt.Errorf("failed to unmarshal processes JSON: %w", err)
	}

	return processes, nil
}

// Helper function to get sorted keys from a map for debugging
func getMapKeys(m map[string]interface{}) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// Window represents a window in the system
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

func TestWindow_WindowOperations(t *testing.T) {
	// Initialize AgentBay client
	apiKey := testutil.GetTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for window operations testing...")
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

	// Test window operations
	if session.Window != nil && session.Application != nil {
		// First, start Google Chrome
		fmt.Println("Starting Google Chrome application...")
		startCmd := "/usr/bin/google-chrome-stable"
		processesStr, err := session.Application.StartApp(startCmd, "")
		if err != nil {
			t.Logf("Note: Failed to start Google Chrome: %v", err)
			t.Logf("Continuing with existing windows...")
		} else {
			// Parse the processes string into Process objects
			chromeProcesses, parseErr := extractProcesses(processesStr)
			if parseErr != nil {
				t.Logf("Warning: Failed to parse processes: %v", parseErr)
				t.Logf("Continuing with existing windows...")
			} else {
				t.Logf("Google Chrome started successfully, returned %d processes", len(chromeProcesses))

				// Give Chrome some time to initialize
				time.Sleep(10 * time.Second)

				// Clean up Chrome processes at the end
				defer func() {
					for _, proc := range chromeProcesses {
						if proc.PID > 0 {
							fmt.Printf("Attempting to stop Chrome process (PID: %d)...\n", proc.PID)
							stopErr, _ := session.Application.StopAppByPID(proc.PID)
							if stopErr != "" {
								t.Logf("Warning: Failed to stop Chrome process: %v", stopErr)
							} else {
								t.Logf("Successfully stopped Chrome process (PID: %d)", proc.PID)
							}
						}
					}
				}()
			}
		}

		// Get a list of root windows
		rootWindowsResponse, err := session.Window.ListRootWindows()
		if err != nil {
			t.Logf("Note: ListRootWindows failed: %v", err)
			return
		}

		// Debug the response structure
		t.Logf("ListRootWindows response type: %T", rootWindowsResponse)

		// Extract windows from the response content
		windows, err := extractWindowsFromContent(rootWindowsResponse)
		if err != nil {
			t.Logf("Note: Failed to extract windows: %v", err)
			return
		}

		// Convert windows to a slice of interfaces for compatibility with the rest of the code
		rootWindowsSlice := make([]interface{}, len(windows))
		for i, window := range windows {
			// Convert each Window struct to a map[string]interface{}
			windowMap := map[string]interface{}{
				"window_id": float64(window.WindowID),
				"title":     window.Title,
				"pid":       float64(window.PID),
				"pname":     window.PName,
			}
			rootWindowsSlice[i] = windowMap
		}

		if len(rootWindowsSlice) == 0 {
			t.Logf("No windows available for testing window operations")
			return
		}

		// Try to find a Chrome window for testing
		var windowID int
		var windowFound bool
		for _, windowInterface := range rootWindowsSlice {
			window, ok := windowInterface.(map[string]interface{})
			if !ok {
				t.Logf("Window is not a map: %T", windowInterface)
				continue
			}

			// Debug the window structure
			t.Logf("Window keys: %v", getMapKeys(window))

			// Check for both "pname" and "PName" since the case might vary
			var pName string
			if pNameVal, ok := window["pname"].(string); ok {
				pName = pNameVal
			} else if pNameVal, ok := window["PName"].(string); ok {
				pName = pNameVal
			} else {
				t.Logf("Window missing pname field: %v", window)
				continue
			}

			if pName == "chrome" {
				// Check for both "window_id" and "WindowID"
				var windowIDVal float64
				var idFound bool

				if idVal, ok := window["window_id"].(float64); ok {
					windowIDVal = idVal
					idFound = true
				} else if idVal, ok := window["WindowID"].(float64); ok {
					windowIDVal = idVal
					idFound = true
				} else {
					t.Logf("Chrome window missing window_id field: %v", window)
					continue
				}

				if idFound {
					windowID = int(windowIDVal)
					windowFound = true
					t.Logf("Found Chrome window with ID %d for testing window operations", windowID)
					break
				}
			}
		}

		// If no Chrome window found, use the first window
		if !windowFound && len(rootWindowsSlice) > 0 {
			firstWindow, ok := rootWindowsSlice[0].(map[string]interface{})
			if ok {
				// Check for both "window_id" and "WindowID"
				var windowIDVal float64
				var idFound bool

				if idVal, ok := firstWindow["window_id"].(float64); ok {
					windowIDVal = idVal
					idFound = true
				} else if idVal, ok := firstWindow["WindowID"].(float64); ok {
					windowIDVal = idVal
					idFound = true
				}

				if idFound {
					windowID = int(windowIDVal)
					t.Logf("No Chrome window found, using window with ID %d for testing window operations", windowID)
					windowFound = true
				} else {
					t.Logf("First window missing window_id field: %v", firstWindow)
				}
			}
		}

		if !windowFound {
			t.Logf("No suitable windows found for testing")
			return
		}

		// Test RestoreWindow
		fmt.Printf("Restoring window with ID %d...\n", windowID)
		err = session.Window.RestoreWindow(windowID)
		if err != nil {
			t.Logf("Note: RestoreWindow failed: %v", err)
		} else {
			t.Logf("Window restored successfully")
		}
		// Wait for 3 seconds to allow user to see the result
		time.Sleep(3 * time.Second)

		// Test ResizeWindow
		fmt.Printf("Resizing window with ID %d to 800x600...\n", windowID)
		err = session.Window.ResizeWindow(windowID, 800, 600)
		if err != nil {
			t.Logf("Note: ResizeWindow failed: %v", err)
		} else {
			t.Logf("Window resized successfully")
		}
		// Wait for 3 seconds to allow user to see the result
		time.Sleep(3 * time.Second)

		// Test MinimizeWindow
		fmt.Printf("Minimizing window with ID %d...\n", windowID)
		err = session.Window.MinimizeWindow(windowID)
		if err != nil {
			t.Logf("Note: MinimizeWindow failed: %v", err)
		} else {
			t.Logf("Window minimized successfully")
		}
		// Wait for 3 seconds to allow user to see the result
		time.Sleep(3 * time.Second)

		// Test MaximizeWindow
		fmt.Printf("Maximizing window with ID %d...\n", windowID)
		err = session.Window.MaximizeWindow(windowID)
		if err != nil {
			t.Logf("Note: MaximizeWindow failed: %v", err)
		} else {
			t.Logf("Window maximized successfully")
		}
		// Wait for 3 seconds to allow user to see the result
		time.Sleep(3 * time.Second)

		// Start a terminal
		fmt.Println("Starting gnome-terminal...")
		terminalProcessesStr, err := session.Application.StartApp("/usr/bin/gnome-terminal", "")
		if err != nil {
			t.Logf("Note: Failed to start gnome-terminal: %v", err)
		} else {
			// Parse the processes string into Process objects
			terminalProcesses, parseErr := extractProcesses(terminalProcessesStr)
			if parseErr != nil {
				t.Logf("Warning: Failed to parse terminal processes: %v", parseErr)
			} else {
				t.Logf("Terminal started successfully, returned %d processes", len(terminalProcesses))

				// Give terminal some time to initialize
				time.Sleep(3 * time.Second)

				// Clean up terminal processes at the end
				defer func() {
					for _, proc := range terminalProcesses {
						if proc.PID > 0 {
							fmt.Printf("Attempting to stop terminal process (PID: %d)...\n", proc.PID)
							stopErr, _ := session.Application.StopAppByPID(proc.PID)
							if stopErr != "" {
								t.Logf("Warning: Failed to stop terminal process: %v", stopErr)
							} else {
								t.Logf("Successfully stopped terminal process (PID: %d)", proc.PID)
							}
						}
					}
				}()
			}
		}

		// Activate the Chrome window again
		fmt.Printf("Activating Chrome window with ID %d again...\n", windowID)
		err = session.Window.ActivateWindow(windowID)
		if err != nil {
			t.Logf("Note: ActivateWindow failed: %v", err)
		} else {
			t.Logf("Window activated successfully")
		}
		// Wait for 3 seconds to allow user to see the result
		time.Sleep(3 * time.Second)

		// Test FullscreenWindow
		fmt.Printf("Fullscreening window with ID %d...\n", windowID)
		err = session.Window.FullscreenWindow(windowID)
		if err != nil {
			t.Logf("Note: FullscreenWindow failed: %v", err)
		} else {
			t.Logf("Window fullscreened successfully")
		}
		// Wait for 3 seconds to allow user to see the result
		time.Sleep(3 * time.Second)

		// Test CloseWindow
		fmt.Printf("Closing window with ID %d...\n", windowID)
		err = session.Window.CloseWindow(windowID)
		if err != nil {
			t.Logf("Note: CloseWindow failed: %v", err)
		} else {
			t.Logf("Window closed successfully")
		}
		// Wait for 3 seconds to allow user to see the result
		time.Sleep(3 * time.Second)
	} else {
		t.Logf("Note: Window interface is nil, skipping window operations test")
	}
}
