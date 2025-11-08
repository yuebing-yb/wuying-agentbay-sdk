# Class: Computer

## 🖥️ Related Tutorial

- [Computer Use Guide](../../../../../docs/guides/computer-use/README.md) - Automate desktop applications

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

### Constructors

- [constructor](computer.md#constructor)

### Methods

- [activateWindow](computer.md#activatewindow)
- [clickMouse](computer.md#clickmouse)
- [closeWindow](computer.md#closewindow)
- [dragMouse](computer.md#dragmouse)
- [focusMode](computer.md#focusmode)
- [fullscreenWindow](computer.md#fullscreenwindow)
- [getActiveWindow](computer.md#getactivewindow)
- [getCursorPosition](computer.md#getcursorposition)
- [getInstalledApps](computer.md#getinstalledapps)
- [getScreenSize](computer.md#getscreensize)
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

## Constructors

### constructor

• **new Computer**(`session`): [`Computer`](computer.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `session` | `ComputerSession` |

#### Returns

[`Computer`](computer.md)

## Methods

### activateWindow

▸ **activateWindow**(`windowId`): `Promise`\<`BoolResult`\>

Activates the specified window.

#### Parameters

| Name | Type |
| :------ | :------ |
| `windowId` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

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

| Name | Type |
| :------ | :------ |
| `windowId` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

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

| Name | Type |
| :------ | :------ |
| `on` | `boolean` |

#### Returns

`Promise`\<`BoolResult`\>

___

### fullscreenWindow

▸ **fullscreenWindow**(`windowId`): `Promise`\<`BoolResult`\>

Makes the specified window fullscreen.

#### Parameters

| Name | Type |
| :------ | :------ |
| `windowId` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

___

### getActiveWindow

▸ **getActiveWindow**(`timeoutMs?`): `Promise`\<`WindowInfoResult`\>

Gets the currently active window.

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `timeoutMs` | `number` | `3000` |

#### Returns

`Promise`\<`WindowInfoResult`\>

___

### getCursorPosition

▸ **getCursorPosition**(): `Promise`\<`CursorPosition`\>

Get cursor position.

#### Returns

`Promise`\<`CursorPosition`\>

Promise resolving to result containing cursor coordinates

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateGetCursorPosition() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Get current cursor position
      const positionResult = await session.computer.getCursorPosition();
      if (positionResult.success) {
        console.log(`Cursor at: (${positionResult.x}, ${positionResult.y})`);
      } else {
        console.log(`Failed to get cursor position: ${positionResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateGetCursorPosition().catch(console.error);
```

___

### getInstalledApps

▸ **getInstalledApps**(`startMenu?`, `desktop?`, `ignoreSystemApps?`): `Promise`\<`any`\>

Gets the list of installed applications.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `startMenu` | `boolean` | `true` | Whether to include applications from start menu (default: true) |
| `desktop` | `boolean` | `false` | Whether to include applications from desktop (default: false) |
| `ignoreSystemApps` | `boolean` | `true` | Whether to exclude system applications (default: true) |

#### Returns

`Promise`\<`any`\>

Promise resolving to result containing array of installed applications

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateGetInstalledApps() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success) {
      const session = result.session;

      // Get installed applications from start menu
      const appsResult = await session.computer.getInstalledApps();
      if (appsResult.success) {
        console.log(`Found ${appsResult.data.length} installed applications`);
        // Output: Found 15 installed applications
        appsResult.data.forEach(app => {
          console.log(`  - ${app.name}: ${app.path}`);
        });
        // Output:   - Notepad: C:\Windows\System32\notepad.exe
        // Output:   - Calculator: calculator:
      }

      // Get applications including desktop shortcuts
      const desktopAppsResult = await session.computer.getInstalledApps(true, true, true);
      if (desktopAppsResult.success) {
        console.log(`Found ${desktopAppsResult.data.length} applications (including desktop)`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateGetInstalledApps().catch(console.error);
```

___

### getScreenSize

▸ **getScreenSize**(): `Promise`\<`ScreenSize`\>

Get screen size.

#### Returns

`Promise`\<`ScreenSize`\>

Promise resolving to result containing screen dimensions and DPI scaling

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateGetScreenSize() {
  try {
    const result = await agentBay.create({
      imageId: 'windows_latest'
    });
    if (result.success && result.session) {
      const session = result.session;

      // Get screen size and DPI information
      const sizeResult = await session.computer.getScreenSize();
      if (sizeResult.success) {
        console.log(`Screen: ${sizeResult.width}x${sizeResult.height}, DPI: ${sizeResult.dpiScalingFactor}`);
      } else {
        console.log(`Failed to get screen size: ${sizeResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateGetScreenSize().catch(console.error);
```

___

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

| Name | Type | Default value |
| :------ | :------ | :------ |
| `timeoutMs` | `number` | `3000` |

#### Returns

`Promise`\<`WindowListResult`\>

___

### listVisibleApps

▸ **listVisibleApps**(): `Promise`\<`any`\>

Lists all visible applications.

#### Returns

`Promise`\<`any`\>

___

### maximizeWindow

▸ **maximizeWindow**(`windowId`): `Promise`\<`BoolResult`\>

Maximizes the specified window.

#### Parameters

| Name | Type |
| :------ | :------ |
| `windowId` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

___

### minimizeWindow

▸ **minimizeWindow**(`windowId`): `Promise`\<`BoolResult`\>

Minimizes the specified window.

#### Parameters

| Name | Type |
| :------ | :------ |
| `windowId` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

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

| Name | Type |
| :------ | :------ |
| `windowId` | `number` |
| `width` | `number` |
| `height` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

___

### restoreWindow

▸ **restoreWindow**(`windowId`): `Promise`\<`BoolResult`\>

Restores the specified window.

#### Parameters

| Name | Type |
| :------ | :------ |
| `windowId` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

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

| Name | Type | Default value |
| :------ | :------ | :------ |
| `startCmd` | `string` | `undefined` |
| `workDirectory` | `string` | `""` |
| `activity` | `string` | `""` |

#### Returns

`Promise`\<`any`\>

___

### stopAppByCmd

▸ **stopAppByCmd**(`cmd`): `Promise`\<`any`\>

Stops an application by stop command.

#### Parameters

| Name | Type |
| :------ | :------ |
| `cmd` | `string` |

#### Returns

`Promise`\<`any`\>

___

### stopAppByPID

▸ **stopAppByPID**(`pid`): `Promise`\<`any`\>

Stops an application by process ID.

#### Parameters

| Name | Type |
| :------ | :------ |
| `pid` | `number` |

#### Returns

`Promise`\<`any`\>

___

### stopAppByPName

▸ **stopAppByPName**(`pname`): `Promise`\<`any`\>

Stops an application by process name.

#### Parameters

| Name | Type |
| :------ | :------ |
| `pname` | `string` |

#### Returns

`Promise`\<`any`\>

## Best Practices

1. Verify screen coordinates before mouse operations
2. Use appropriate delays between UI interactions
3. Handle window focus changes properly
4. Take screenshots for verification and debugging
5. Use keyboard shortcuts for efficient automation
6. Clean up windows and applications after automation


## Related Resources

- [Application API Reference](application.md)
- [UI API Reference](ui.md)
- [Window API Reference](window.md)

