# Class: Computer

## 🖥️ Related Tutorial

- [Computer Use Guide](../../../../docs/guides/computer-use/README.md) - Automate desktop applications

## Overview

The Computer module provides comprehensive desktop automation capabilities including mouse operations,
keyboard input, screen capture, and window management. It enables automated UI testing and RPA workflows.


## Requirements

- Requires `windows_latest` image for computer use features

## Data Types

### MouseButton

Mouse button constants: Left, Right, Middle

### ScrollDirection

Scroll direction constants: Up, Down, Left, Right

### KeyModifier

Keyboard modifier keys: Ctrl, Alt, Shift, Win

## Important Notes

- Key names in PressKeys and ReleaseKeys are case-sensitive
- Coordinate validation: x and y must be non-negative integers
- Drag operation requires valid start and end coordinates
- Screenshot operations may have size limitations

## Table of contents


### Methods

- [activateWindow](computer.md#activatewindow)
- [clickMouse](computer.md#clickmouse)
- [closeWindow](computer.md#closewindow)
- [dragMouse](computer.md#dragmouse)
- [focusMode](computer.md#focusmode)
- [fullscreenWindow](computer.md#fullscreenwindow)
- [inputText](computer.md#inputtext)
- [listRootWindows](computer.md#listrootwindows)
- [listVisibleApps](computer.md#listvisibleapps)
- [maximizeWindow](computer.md#maximizewindow)
- [minimizeWindow](computer.md#minimizewindow)
- [moveMouse](computer.md#movemouse)
- [pressKeys](computer.md#presskeys)
- [releaseKeys](computer.md#releasekeys)
- [resizeWindow](computer.md#resizewindow)
- [restoreWindow](computer.md#restorewindow)
- [screenshot](computer.md#screenshot)
- [scroll](computer.md#scroll)
- [startApp](computer.md#startapp)
- [stopAppByCmd](computer.md#stopappbycmd)
- [stopAppByPID](computer.md#stopappbypid)
- [stopAppByPName](computer.md#stopappbypname)

## Methods

### activateWindow

▸ **activateWindow**(`windowId`): `Promise`\<`BoolResult`\>

Activates the specified window.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | ID of the window to activate |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateActivateWindow() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success) {
      const session = result.session;

      // List all windows
      const windows = await session.computer.listRootWindows();
      if (windows.success && windows.windows.length > 0) {
        const windowId = windows.windows[0].id;

        // Activate the first window
        const activateResult = await session.computer.activateWindow(windowId);
        if (activateResult.success) {
          console.log(`Window ${windowId} activated successfully`);
          // Output: Window 12345 activated successfully
        } else {
          console.log(`Failed to activate window: ${activateResult.errorMessage}`);
        }
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateActivateWindow().catch(console.error);
```

___

### clickMouse

▸ **clickMouse**(`x`, `y`, `button?`): `Promise`\<`BoolResult`\>

Click mouse at specified coordinates.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `x` | `number` | `undefined` | X coordinate for the click |
| `y` | `number` | `undefined` | Y coordinate for the click |
| `button` | `string` | `MouseButton.LEFT` | Mouse button to click (default: 'left'). Valid values: 'left', 'right', 'middle', 'double_left' |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateClickMouse() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success) {
      const session = result.session;

      // Click at coordinates (100, 100) with left button
      const clickResult = await session.computer.clickMouse(100, 100, 'left');
      if (clickResult.success) {
        console.log('Mouse clicked successfully');
      } else {
        console.log(`Click failed: ${clickResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateClickMouse().catch(console.error);
```

___

### closeWindow

▸ **closeWindow**(`windowId`): `Promise`\<`BoolResult`\>

Closes the specified window.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | ID of the window to close |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateCloseWindow() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Start an application
      await session.computer.startApp('notepad.exe');

      // Get the active window
      const activeWindow = await session.computer.getActiveWindow();
      if (activeWindow.success && activeWindow.window) {
        // Close the window
        const closeResult = await session.computer.closeWindow(activeWindow.window.id);
        if (closeResult.success) {
          console.log('Window closed successfully');
        } else {
          console.log(`Failed to close window: ${closeResult.errorMessage}`);
        }
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateCloseWindow().catch(console.error);
```

___

### dragMouse

▸ **dragMouse**(`fromX`, `fromY`, `toX`, `toY`, `button?`): `Promise`\<`BoolResult`\>

Drag mouse from one position to another.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `fromX` | `number` | `undefined` | Starting X coordinate |
| `fromY` | `number` | `undefined` | Starting Y coordinate |
| `toX` | `number` | `undefined` | Ending X coordinate |
| `toY` | `number` | `undefined` | Ending Y coordinate |
| `button` | `string` | `MouseButton.LEFT` | Mouse button to use for drag (default: 'left'). Valid values: 'left', 'right', 'middle' |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateDragMouse() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Drag from (100, 100) to (300, 300) with left button
      const dragResult = await session.computer.dragMouse(100, 100, 300, 300, 'left');
      if (dragResult.success) {
        console.log('Drag operation completed successfully');
      } else {
        console.log(`Drag failed: ${dragResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateDragMouse().catch(console.error);
```

___

### focusMode

▸ **focusMode**(`on`): `Promise`\<`BoolResult`\>

Toggles focus mode on or off.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `on` | `boolean` | Whether to enable (true) or disable (false) focus mode |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateFocusMode() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Enable focus mode
      const enableResult = await session.computer.focusMode(true);
      if (enableResult.success) {
        console.log('Focus mode enabled');
      }

      // Do some work...

      // Disable focus mode
      const disableResult = await session.computer.focusMode(false);
      if (disableResult.success) {
        console.log('Focus mode disabled');
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateFocusMode().catch(console.error);
```

___

### fullscreenWindow

▸ **fullscreenWindow**(`windowId`): `Promise`\<`BoolResult`\>

Makes the specified window fullscreen.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | ID of the window to make fullscreen |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateFullscreenWindow() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Start an application
      await session.computer.startApp('notepad.exe');

      // Get the active window
      const activeWindow = await session.computer.getActiveWindow();
      if (activeWindow.success && activeWindow.window) {
        // Make the window fullscreen
        const fullscreenResult = await session.computer.fullscreenWindow(activeWindow.window.id);
        if (fullscreenResult.success) {
          console.log('Window set to fullscreen successfully');
        } else {
          console.log(`Failed to set window fullscreen: ${fullscreenResult.errorMessage}`);
        }
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateFullscreenWindow().catch(console.error);
```

### inputText

▸ **inputText**(`text`): `Promise`\<`BoolResult`\>

Input text at the current cursor position.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `text` | `string` | Text to input |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateInputText() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Input text at current cursor position
      const inputResult = await session.computer.inputText('Hello AgentBay!');
      if (inputResult.success) {
        console.log('Text input successfully');
      } else {
        console.log(`Input failed: ${inputResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateInputText().catch(console.error);
```

___

### listRootWindows

▸ **listRootWindows**(`timeoutMs?`): `Promise`\<`WindowListResult`\>

Lists all root windows.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `timeoutMs` | `number` | `3000` | Timeout in milliseconds (default: 3000) |

#### Returns

`Promise`\<`WindowListResult`\>

Promise resolving to result containing array of root windows

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateListRootWindows() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // List all root windows
      const windowsResult = await session.computer.listRootWindows();
      if (windowsResult.success) {
        console.log(`Found ${windowsResult.windows.length} root windows`);
        windowsResult.windows.forEach(win => {
          console.log(`  - Window ${win.id}: ${win.title}`);
        });
      } else {
        console.log(`Failed to list windows: ${windowsResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateListRootWindows().catch(console.error);
```

___

### listVisibleApps

▸ **listVisibleApps**(): `Promise`\<`any`\>

Lists all visible applications.

#### Returns

`Promise`\<`any`\>

Promise resolving to result containing array of visible application processes

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateListVisibleApps() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success) {
      const session = result.session;

      // List all visible applications
      const appsResult = await session.computer.listVisibleApps();
      if (appsResult.success) {
        console.log(`Found ${appsResult.data.length} visible applications`);
        // Output: Found 5 visible applications
        appsResult.data.forEach(app => {
          console.log(`  - PID ${app.pid}: ${app.name}`);
        });
        // Output:   - PID 1234: notepad.exe
        // Output:   - PID 5678: chrome.exe
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateListVisibleApps().catch(console.error);
```

___

### maximizeWindow

▸ **maximizeWindow**(`windowId`): `Promise`\<`BoolResult`\>

Maximizes the specified window.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | ID of the window to maximize |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateMaximizeWindow() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Start an application
      await session.computer.startApp('notepad.exe');

      // Get the active window
      const activeWindow = await session.computer.getActiveWindow();
      if (activeWindow.success && activeWindow.window) {
        // Maximize the window
        const maxResult = await session.computer.maximizeWindow(activeWindow.window.id);
        if (maxResult.success) {
          console.log('Window maximized successfully');
        } else {
          console.log(`Failed to maximize window: ${maxResult.errorMessage}`);
        }
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateMaximizeWindow().catch(console.error);
```

___

### minimizeWindow

▸ **minimizeWindow**(`windowId`): `Promise`\<`BoolResult`\>

Minimizes the specified window.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | ID of the window to minimize |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateMinimizeWindow() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Start an application
      await session.computer.startApp('notepad.exe');

      // Get the active window
      const activeWindow = await session.computer.getActiveWindow();
      if (activeWindow.success && activeWindow.window) {
        // Minimize the window
        const minResult = await session.computer.minimizeWindow(activeWindow.window.id);
        if (minResult.success) {
          console.log('Window minimized successfully');
        } else {
          console.log(`Failed to minimize window: ${minResult.errorMessage}`);
        }
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateMinimizeWindow().catch(console.error);
```

___

### moveMouse

▸ **moveMouse**(`x`, `y`): `Promise`\<`BoolResult`\>

Move mouse to specified coordinates.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `x` | `number` | X coordinate to move to |
| `y` | `number` | Y coordinate to move to |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateMoveMouse() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Move mouse to coordinates (300, 400)
      const moveResult = await session.computer.moveMouse(300, 400);
      if (moveResult.success) {
        console.log('Mouse moved successfully');

        // Verify new position
        const pos = await session.computer.getCursorPosition();
        console.log(`New position: (${pos.x}, ${pos.y})`);
      } else {
        console.log(`Move failed: ${moveResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateMoveMouse().catch(console.error);
```

___

### pressKeys

▸ **pressKeys**(`keys`, `hold?`): `Promise`\<`BoolResult`\>

Press one or more keys.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `keys` | `string`[] | `undefined` | Array of key names to press |
| `hold` | `boolean` | `false` | Whether to hold the keys down (default: false) |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstratePressKeys() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Press Enter key
      const enterResult = await session.computer.pressKeys(['Enter']);
      if (enterResult.success) {
        console.log('Enter key pressed successfully');
      }

      // Press Ctrl+C (hold the keys)
      const ctrlCResult = await session.computer.pressKeys(['Ctrl', 'c'], true);
      if (ctrlCResult.success) {
        console.log('Ctrl+C pressed successfully');
        // Remember to release the keys
        await session.computer.releaseKeys(['Ctrl', 'c']);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstratePressKeys().catch(console.error);
```

___

### releaseKeys

▸ **releaseKeys**(`keys`): `Promise`\<`BoolResult`\>

Release previously pressed keys.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `keys` | `string`[] | Array of key names to release |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateReleaseKeys() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Press and hold Ctrl key
      await session.computer.pressKeys(['Ctrl'], true);

      // Release Ctrl key
      const releaseResult = await session.computer.releaseKeys(['Ctrl']);
      if (releaseResult.success) {
        console.log('Ctrl key released successfully');
      } else {
        console.log(`Release failed: ${releaseResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateReleaseKeys().catch(console.error);
```

___

### resizeWindow

▸ **resizeWindow**(`windowId`, `width`, `height`): `Promise`\<`BoolResult`\>

Resizes the specified window.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | ID of the window to resize |
| `width` | `number` | New width of the window |
| `height` | `number` | New height of the window |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateResizeWindow() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Start an application
      await session.computer.startApp('notepad.exe');

      // Get the active window
      const activeWindow = await session.computer.getActiveWindow();
      if (activeWindow.success && activeWindow.window) {
        // Resize the window to 800x600
        const resizeResult = await session.computer.resizeWindow(activeWindow.window.id, 800, 600);
        if (resizeResult.success) {
          console.log('Window resized successfully to 800x600');
        } else {
          console.log(`Failed to resize window: ${resizeResult.errorMessage}`);
        }
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateResizeWindow().catch(console.error);
```

___

### restoreWindow

▸ **restoreWindow**(`windowId`): `Promise`\<`BoolResult`\>

Restores the specified window.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | ID of the window to restore |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateRestoreWindow() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Start an application and minimize it
      await session.computer.startApp('notepad.exe');
      const activeWindow = await session.computer.getActiveWindow();
      if (activeWindow.success && activeWindow.window) {
        await session.computer.minimizeWindow(activeWindow.window.id);

        // Restore the window
        const restoreResult = await session.computer.restoreWindow(activeWindow.window.id);
        if (restoreResult.success) {
          console.log('Window restored successfully');
        } else {
          console.log(`Failed to restore window: ${restoreResult.errorMessage}`);
        }
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateRestoreWindow().catch(console.error);
```

___

### screenshot

▸ **screenshot**(): `Promise`\<`ScreenshotResult`\>

Take a screenshot.

#### Returns

`Promise`\<`ScreenshotResult`\>

Promise resolving to result containing screenshot URL

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateScreenshot() {
    try {
        const result = await agentBay.create({
            imageId: 'windows_latest'
        });
        if (result.success && result.session) {
            const session = result.session;

            // Take a screenshot
            const screenshotResult = await session.computer.screenshot();
            if (screenshotResult.success) {
                console.log('Screenshot taken successfully');
                console.log(`Screenshot URL: ${screenshotResult.data}`);
            } else {
                console.log(`Screenshot failed: ${screenshotResult.errorMessage}`);
            }

            await session.delete();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

demonstrateScreenshot().catch(console.error);
```

___

### scroll

▸ **scroll**(`x`, `y`, `direction?`, `amount?`): `Promise`\<`BoolResult`\>

Scroll at specified coordinates.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `x` | `number` | `undefined` | X coordinate to scroll at |
| `y` | `number` | `undefined` | Y coordinate to scroll at |
| `direction` | `string` | `ScrollDirection.UP` | Scroll direction (default: 'up'). Valid values: 'up', 'down', 'left', 'right' |
| `amount` | `number` | `1` | Scroll amount (default: 1) |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateScroll() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Scroll up at center of screen, amount 3
      const scrollResult = await session.computer.scroll(400, 300, 'up', 3);
      if (scrollResult.success) {
        console.log('Scroll completed successfully');
      } else {
        console.log(`Scroll failed: ${scrollResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateScroll().catch(console.error);
```

___

### startApp

▸ **startApp**(`startCmd`, `workDirectory?`, `activity?`): `Promise`\<`any`\>

Starts the specified application.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `startCmd` | `string` | `undefined` | The command to start the application (e.g., 'notepad.exe', 'calculator:') |
| `workDirectory` | `string` | `""` | The working directory for the application (optional) |
| `activity` | `string` | `""` | The activity parameter (optional, primarily for mobile use) |

#### Returns

`Promise`\<`any`\>

Promise resolving to result containing array of started processes

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateStartApp() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success) {
      const session = result.session;

      // Start Notepad application
      const startResult = await session.computer.startApp('notepad.exe');
      if (startResult.success) {
        console.log(`Started ${startResult.data.length} process(es)`);
        // Output: Started 1 process(es)
        startResult.data.forEach(proc => {
          console.log(`  - PID ${proc.pid}: ${proc.name}`);
        });
        // Output:   - PID 1234: notepad.exe
      } else {
        console.log(`Failed to start app: ${startResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateStartApp().catch(console.error);
```

___

### stopAppByCmd

▸ **stopAppByCmd**(`cmd`): `Promise`\<`any`\>

Stops an application by stop command.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `cmd` | `string` | The command to stop the application |

#### Returns

`Promise`\<`any`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateStopAppByCmd() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success) {
      const session = result.session;

      // Start an application first
      await session.computer.startApp('notepad.exe');

      // Stop the application using a command
      const stopResult = await session.computer.stopAppByCmd('taskkill /IM notepad.exe /F');
      if (stopResult.success) {
        console.log('Application stopped successfully using command');
        // Output: Application stopped successfully using command
      } else {
        console.log(`Failed to stop app: ${stopResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateStopAppByCmd().catch(console.error);
```

___

### stopAppByPID

▸ **stopAppByPID**(`pid`): `Promise`\<`any`\>

Stops an application by process ID.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `pid` | `number` | The process ID to stop |

#### Returns

`Promise`\<`any`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateStopAppByPID() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success) {
      const session = result.session;

      // Start an application and get its PID
      const startResult = await session.computer.startApp('notepad.exe');
      if (startResult.success && startResult.data.length > 0) {
        const pid = startResult.data[0].pid;
        console.log(`Started application with PID: ${pid}`);

        // Stop the application by PID
        const stopResult = await session.computer.stopAppByPID(pid);
        if (stopResult.success) {
          console.log(`Application with PID ${pid} stopped successfully`);
          // Output: Application with PID 1234 stopped successfully
        } else {
          console.log(`Failed to stop app: ${stopResult.errorMessage}`);
        }
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateStopAppByPID().catch(console.error);
```

___

### stopAppByPName

▸ **stopAppByPName**(`pname`): `Promise`\<`any`\>

Stops an application by process name.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `pname` | `string` | The process name to stop (e.g., 'notepad.exe', 'chrome.exe') |

#### Returns

`Promise`\<`any`\>

Promise resolving to result with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateStopAppByPName() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success) {
      const session = result.session;

      // Start an application first
      await session.computer.startApp('notepad.exe');

      // Stop the application by process name
      const stopResult = await session.computer.stopAppByPName('notepad.exe');
      if (stopResult.success) {
        console.log('Application stopped successfully');
        // Output: Application stopped successfully
      } else {
        console.log(`Failed to stop app: ${stopResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateStopAppByPName().catch(console.error);
```

## Best Practices

1. Verify screen coordinates before mouse operations
2. Use appropriate delays between UI interactions
3. Handle window focus changes properly
4. Take screenshots for verification and debugging
5. Use keyboard shortcuts for efficient automation
6. Clean up windows and applications after automation

