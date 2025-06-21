package main

import (
	"encoding/base64"
	"fmt"
	"os"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/ui"
)

func main() {
	// Get API key from environment variable or use a default value for testing
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		apiKey = "akm-xxx" // Replace with your actual API key for testing
		fmt.Println("Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for production use.")
	}

	// Initialize the AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	// Create session parameters with ImageId set to mobile_latest for UI operations
	params := agentbay.NewCreateSessionParams().WithImageId("mobile_latest")

	// Create a new session
	fmt.Println("\nCreating a new session with mobile_latest image...")
	session, err := agentBay.Create(params)
	if err != nil {
		fmt.Printf("\nError creating session: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("\nSession created with ID: %s\n", session.SessionID)
	defer func() {
		// Clean up by deleting the session when we're done
		fmt.Println("\nDeleting the session...")
		err = agentBay.Delete(session)
		if err != nil {
			fmt.Printf("Error deleting session: %v\n", err)
		} else {
			fmt.Println("Session deleted successfully")
		}
	}()

	// 1. Take a screenshot
	fmt.Println("\n1. Taking a screenshot...")
	screenshot, err := session.UI.Screenshot()
	if err != nil {
		fmt.Printf("Error taking screenshot: %v\n", err)
	} else {
		// The screenshot is returned as a base64-encoded string
		fmt.Printf("Screenshot taken successfully. Base64 data length: %d bytes\n", len(screenshot))

		// Optional: Save the screenshot to a file
		// Uncomment the following lines to save the screenshot
		/*
			imgData, err := base64.StdEncoding.DecodeString(screenshot)
			if err == nil {
				timestamp := time.Now().Format("20060102_150405")
				filename := fmt.Sprintf("screenshot_%s.png", timestamp)
				err = os.WriteFile(filename, imgData, 0644)
				if err == nil {
					fmt.Printf("Screenshot saved to %s\n", filename)
				}
			}
		*/
	}

	// 2. Get all UI elements
	fmt.Println("\n2. Getting all UI elements...")
	elements, err := session.UI.GetAllUIElements(2000) // 2 second timeout
	if err != nil {
		fmt.Printf("Error getting UI elements: %v\n", err)
	} else {
		fmt.Printf("Found %d UI elements\n", len(elements))
		// Print details of the first few elements if available
		elementsToShow := 3
		if len(elements) < elementsToShow {
			elementsToShow = len(elements)
		}

		fmt.Println("\nSample of UI elements found:")
		for i := 0; i < elementsToShow; i++ {
			elem := elements[i]
			fmt.Printf("Element #%d:\n", i+1)
			fmt.Printf("  Type: %v\n", elem.Type)
			fmt.Printf("  Text: %v\n", elem.Text)
			fmt.Printf("  Bounds: %v\n", elem.Bounds)
			fmt.Printf("  ResourceId: %v\n", elem.ResourceId)
			fmt.Println()
		}
	}

	// 3. Get clickable UI elements
	fmt.Println("\n3. Getting clickable UI elements...")
	clickableElements, err := session.UI.GetClickableUIElements(2000) // 2 second timeout
	if err != nil {
		fmt.Printf("Error getting clickable UI elements: %v\n", err)
	} else {
		fmt.Printf("Found %d clickable UI elements\n", len(clickableElements))
		// Print details of the first few clickable elements if available
		elementsToShow := 3
		if len(clickableElements) < elementsToShow {
			elementsToShow = len(clickableElements)
		}

		fmt.Println("\nSample of clickable UI elements found:")
		for i := 0; i < elementsToShow; i++ {
			elem := clickableElements[i]
			fmt.Printf("Element #%d:\n", i+1)
			fmt.Printf("  Type: %v\n", elem.Type)
			fmt.Printf("  Text: %v\n", elem.Text)
			fmt.Printf("  Bounds: %v\n", elem.Bounds)
			fmt.Printf("  ResourceId: %v\n", elem.ResourceId)
			fmt.Println()
		}
	}

	// 4. Send key event (HOME key)
	fmt.Println("\n4. Sending HOME key event...")
	result, err := session.UI.SendKey(ui.KeyCode.HOME) // Use KeyCode.HOME constant
	if err != nil {
		fmt.Printf("Error sending HOME key: %v\n", err)
	} else {
		fmt.Println("HOME key sent successfully, response:", result)
	}

	// Sleep briefly to allow UI to update after HOME key
	time.Sleep(1 * time.Second)

	// 5. Input text
	fmt.Println("\n5. Inputting text...")
	response, err := session.UI.InputText("Hello from AgentBay SDK!")
	if err != nil {
		fmt.Printf("Error inputting text: %v\n", err)
	} else {
		fmt.Println("Text input successful, response:", response)
	}

	// 6. Click a position on screen
	fmt.Println("\n6. Clicking on screen position...")
	// Coordinates for center of screen (example values)
	x := 540
	y := 960
	clickResponse, err := session.UI.Click(x, y, "left")
	if err != nil {
		fmt.Printf("Error clicking on position (%d,%d): %v\n", x, y, err)
	} else {
		fmt.Printf("Successfully clicked at position (%d,%d), response: %s\n", x, y, clickResponse)
	}

	// Sleep briefly to allow UI to update after click
	time.Sleep(1 * time.Second)

	// 7. Swipe on screen
	fmt.Println("\n7. Performing swipe gesture...")
	startX := 540
	startY := 1500
	endX := 540
	endY := 500
	swipeDuration := 500 // milliseconds
	swipeResponse, err := session.UI.Swipe(startX, startY, endX, endY, swipeDuration)
	if err != nil {
		fmt.Printf("Error performing swipe from (%d,%d) to (%d,%d): %v\n",
			startX, startY, endX, endY, err)
	} else {
		fmt.Printf("Successfully swiped from (%d,%d) to (%d,%d), response: %s\n",
			startX, startY, endX, endY, swipeResponse)
	}

	// 8. Take another screenshot after interactions
	fmt.Println("\n8. Taking another screenshot after interactions...")
	screenshot2, err := session.UI.Screenshot()
	if err != nil {
		fmt.Printf("Error taking second screenshot: %v\n", err)
	} else {
		fmt.Printf("Second screenshot taken successfully. Base64 data length: %d bytes\n", len(screenshot2))

		imgData, err := base64.StdEncoding.DecodeString(screenshot2)
		if err != nil {
			fmt.Printf("Error decoding screenshot: %v\n", err)
		} else {
			// Just inform about the image size
			fmt.Printf("Screenshot image size: %d bytes\n", len(imgData))

			// Uncomment the following lines to save the screenshot
			/*
				// Generate timestamp for unique filename
				timestamp := time.Now().Format("20060102_150405")
				filename := "screenshot_after_" + timestamp + ".png"
				err = os.WriteFile(filename, imgData, 0644)
				if err != nil {
					fmt.Printf("Error saving screenshot: %v\n", err)
				} else {
					fmt.Printf("Screenshot saved to %s\n", filename)
				}
			*/
		}
	}

	fmt.Println("\nUI examples completed successfully!")
}
