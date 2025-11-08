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

| Name | Type | Default value |
| :------ | :------ | :------ |
| `fromX` | `number` | `undefined` |
| `fromY` | `number` | `undefined` |
| `toX` | `number` | `undefined` |
| `toY` | `number` | `undefined` |
| `button` | `string` | `MouseButton.LEFT` |

#### Returns

`Promise`\<`BoolResult`\>

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

___

### inputText

▸ **inputText**(`text`): `Promise`\<`BoolResult`\>

Input text.

#### Parameters

| Name | Type |
| :------ | :------ |
| `text` | `string` |

#### Returns

`Promise`\<`BoolResult`\>

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

| Name | Type |
| :------ | :------ |
| `x` | `number` |
| `y` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

___

### pressKeys

▸ **pressKeys**(`keys`, `hold?`): `Promise`\<`BoolResult`\>

Press keys.

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `keys` | `string`[] | `undefined` |
| `hold` | `boolean` | `false` |

#### Returns

`Promise`\<`BoolResult`\>

___

### releaseKeys

▸ **releaseKeys**(`keys`): `Promise`\<`BoolResult`\>

Release keys.

#### Parameters

| Name | Type |
| :------ | :------ |
| `keys` | `string`[] |

#### Returns

`Promise`\<`BoolResult`\>

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

___

### scroll

▸ **scroll**(`x`, `y`, `direction?`, `amount?`): `Promise`\<`BoolResult`\>

Scroll at specified coordinates.

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `x` | `number` | `undefined` |
| `y` | `number` | `undefined` |
| `direction` | `string` | `ScrollDirection.UP` |
| `amount` | `number` | `1` |

#### Returns

`Promise`\<`BoolResult`\>

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

