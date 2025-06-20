import { AgentBay } from '../../src';
import * as fs from 'fs';

// Helper function to parse bounds from a bounds string like "[0,100][200,300]"
// Returns x1, y1, x2, y2
function parseBounds(boundsStr: string): { x1: number, y1: number, x2: number, y2: number } | null {
  if (!boundsStr || boundsStr.length < 9) {
    return null;
  }

  try {
    // Remove brackets and split by "]["
    const cleaned = boundsStr.substring(1, boundsStr.length - 1);
    const parts = cleaned.split('][');
    if (parts.length !== 2) {
      return null;
    }

    // Parse the coordinates
    const topLeft = parts[0].split(',');
    const bottomRight = parts[1].split(',');

    if (topLeft.length !== 2 || bottomRight.length !== 2) {
      return null;
    }

    return {
      x1: parseInt(topLeft[0], 10),
      y1: parseInt(topLeft[1], 10),
      x2: parseInt(bottomRight[0], 10),
      y2: parseInt(bottomRight[1], 10)
    };
  } catch (error) {
    return null;
  }
}

async function main() {
  // Get API key from environment variable or use default value for testing
  const apiKey = process.env.AGENTBAY_API_KEY || 'akm-xxx'; // Replace with your actual API key for testing
  if (!process.env.AGENTBAY_API_KEY) {
    console.log('Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for production use.');
  }

  // Initialize the AgentBay client
  const agentBay = new AgentBay({ apiKey });

  // Create session parameters with imageId set to mobile_latest for UI operations
  const params = {
    imageId: 'mobile_latest'
  };

  // Create a new session
  console.log('\nCreating a new session with mobile_latest image...');
  const session = await agentBay.create(params);
  console.log(`\nSession created with ID: ${session.sessionId}`);

  try {
    // 1. Take a screenshot using the correct tool name
    console.log('\n1. Taking a screenshot...');
    try {
      // 直接调用底层工具，使用正确的工具名称
      const screenshot = await session.ui.screenshot();
      // The screenshot is returned as a base64-encoded string
      console.log(`Screenshot taken successfully. Base64 data length: ${screenshot.length} bytes`);

      // Optional: Save the screenshot to a file
      // Uncomment the following lines to save the screenshot
      const imgData = Buffer.from(screenshot, 'base64');
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `screenshot_${timestamp}.png`;
      fs.writeFileSync(filename, imgData);
      console.log(`Screenshot saved to ${filename}`);
    } catch (error) {
      console.log(`Error taking screenshot: ${error}`);
    }

    // 2. Get all UI elements
    console.log('\n2. Getting all UI elements...');
    try {
      const elementsJson = await session.ui.getAllUIElements(2000); // 2 second timeout
      // Parse the JSON string to get the actual elements
      const elements = JSON.parse(elementsJson);
      
      console.log(`Found ${elements.length} UI elements`);
      // Print details of the first few elements if available
      const elementsToShow = Math.min(elements.length, 3);
      
      console.log('\nSample of UI elements found:');
      for (let i = 0; i < elementsToShow; i++) {
        const elem = elements[i];
        console.log(`Element #${i+1}:`);
        console.log(`  Type: ${elem.type}`);
        console.log(`  Text: ${elem.text}`);
        console.log(`  Bounds: ${elem.bounds}`);
        console.log(`  ResourceId: ${elem.resourceId}`);
        console.log();
      }
    } catch (error) {
      console.log(`Error getting UI elements: ${error}`);
    }

    // 3. Get clickable UI elements
    console.log('\n3. Getting clickable UI elements...');
    try {
      const clickableElementsJson = await session.ui.getClickableUIElements(2000); // 2 second timeout
      // Parse the JSON string to get the actual elements
      const clickableElements = JSON.parse(clickableElementsJson);
      
      console.log(`Found ${clickableElements.length} clickable UI elements`);
      // Print details of the first few clickable elements if available
      const elementsToShow = Math.min(clickableElements.length, 3);
      
      console.log('\nSample of clickable UI elements found:');
      for (let i = 0; i < elementsToShow; i++) {
        const elem = clickableElements[i];
        console.log(`Element #${i+1}:`);
        console.log(`  Type: ${elem.type}`);
        console.log(`  Text: ${elem.text}`);
        console.log(`  Bounds: ${elem.bounds}`);
        console.log(`  ResourceId: ${elem.resourceId}`);
        console.log();
      }
    } catch (error) {
      console.log(`Error getting clickable UI elements: ${error}`);
    }

    // 4. Send key event (HOME key)
    console.log('\n4. Sending HOME key event...');
    try {
      const resultJson = await session.ui.sendKey(3); // 3 is HOME key code
      // Try to parse the result as a boolean if it's a simple "true" or "false" string
      const success = resultJson === "true" || resultJson === "True";
      console.log(`HOME key sent successfully: ${success}`);
    } catch (error) {
      console.log(`Error sending HOME key: ${error}`);
    }

    // Sleep briefly to allow UI to update after HOME key
    await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second

    // 5. Input text
    console.log('\n5. Inputting text...');
    try {
      const resultText = await session.ui.inputText("Hello from AgentBay SDK!");
      console.log(`Text input successful, result: ${resultText}`);
    } catch (error) {
      console.log(`Error inputting text: ${error}`);
    }

    // 6. Click a position on screen
    console.log('\n6. Clicking on screen position...');
    // Coordinates for center of screen (example values)
    const x = 540;
    const y = 960;
    try {
      const clickResult = await session.ui.click(x, y, "left");
      console.log(`Successfully clicked at position (${x},${y}), result: ${clickResult}`);
    } catch (error) {
      console.log(`Error clicking on position (${x},${y}): ${error}`);
    }

    // Sleep briefly to allow UI to update after click
    await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second

    // 7. Swipe on screen
    console.log('\n7. Performing swipe gesture...');
    const startX = 540;
    const startY = 1500;
    const endX = 540;
    const endY = 500;
    const swipeDuration = 500; // milliseconds
    try {
      const swipeResult = await session.ui.swipe(startX, startY, endX, endY, swipeDuration);
      console.log(`Successfully swiped from (${startX},${startY}) to (${endX},${endY}), result: ${swipeResult}`);
    } catch (error) {
      console.log(`Error performing swipe from (${startX},${startY}) to (${endX},${endY}): ${error}`);
    }

    // 8. Take another screenshot after interactions
    console.log('\n8. Taking another screenshot after interactions...');
    try {
      const screenshot2 = await session.ui.screenshot();
      console.log(`Second screenshot taken successfully. Base64 data length: ${screenshot2.length} bytes`);

      const imgData = Buffer.from(screenshot2, 'base64');
      // Save the second screenshot
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `screenshot_after_${timestamp}.png`;
      fs.writeFileSync(filename, imgData);
      console.log(`Screenshot saved to ${filename}`);
    } catch (error) {
      console.log(`Error taking second screenshot: ${error}`);
    }

    console.log('\nUI examples completed successfully!');

  } finally {
    // Clean up by deleting the session when we're done
    console.log('\nDeleting the session...');
    try {
      await agentBay.delete(session);
      console.log('Session deleted successfully');
    } catch (error) {
      console.log(`Error deleting session: ${error}`);
    }
  }
}

main().catch(error => {
  console.error('Error in main execution:', error);
  process.exit(1);
}); 