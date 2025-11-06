# Class: WindowManager

## 🪟 Related Tutorial

- [Window Management Guide](../../../../../docs/guides/computer-use/window-management.md) - Manage application windows

Handles window management operations in the AgentBay cloud environment.

**`Deprecated`**

This module is deprecated. Use Computer module instead.
- For desktop window operations, use session.computer
- Window operations are not available for mobile

## Table of contents

### Constructors

- [constructor](window.md#constructor)

### Methods

- [activateWindow](window.md#activatewindow)
- [closeWindow](window.md#closewindow)
- [focusMode](window.md#focusmode)
- [fullscreenWindow](window.md#fullscreenwindow)
- [getActiveWindow](window.md#getactivewindow)
- [getWindowInfo](window.md#getwindowinfo)
- [listAllWindows](window.md#listallwindows)
- [listRootWindows](window.md#listrootwindows)
- [maximizeWindow](window.md#maximizewindow)
- [minimizeWindow](window.md#minimizewindow)
- [moveWindow](window.md#movewindow)
- [resizeWindow](window.md#resizewindow)
- [restoreWindow](window.md#restorewindow)

## Constructors

### constructor

• **new WindowManager**(`session`): [`WindowManager`](window.md)

Creates a new WindowManager instance.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `session` | `Object` | The session object that provides access to the AgentBay API. |
| `session.callMcpTool` | (`toolName`: `string`, `args`: `any`) => `Promise`\<\{ `data`: `string` ; `errorMessage`: `string` ; `requestId`: `string` ; `success`: `boolean`  }\> | - |
| `session.getAPIKey` | () => `string` | - |
| `session.getSessionId` | () => `string` | - |

#### Returns

[`WindowManager`](window.md)

## Methods

### activateWindow

▸ **activateWindow**(`windowId`): `Promise`\<`BoolResult`\>

Activates a window by bringing it to the foreground.
Corresponds to Python's activate_window() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | The ID of the window to activate. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Deprecated`**

Use session.computer.activateWindow() instead.

___

### closeWindow

▸ **closeWindow**(`windowId`): `Promise`\<`BoolResult`\>

Closes a window.
Corresponds to Python's close_window() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | The ID of the window to close. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Deprecated`**

Use session.computer.closeWindow() instead.

___

### focusMode

▸ **focusMode**(`on`): `Promise`\<`BoolResult`\>

Enables or disables focus mode.
Corresponds to Python's focus_mode() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `on` | `boolean` | Whether to enable focus mode. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with requestId

___

### fullscreenWindow

▸ **fullscreenWindow**(`windowId`): `Promise`\<`BoolResult`\>

Sets a window to fullscreen by ID.
Corresponds to Python's fullscreen_window() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | The ID of the window to set to fullscreen. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with requestId

___

### getActiveWindow

▸ **getActiveWindow**(`timeoutMs?`): `Promise`\<`WindowInfoResult`\>

Gets the currently active window.
Corresponds to Python's get_active_window() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `timeoutMs` | `number` | `3000` | The timeout in milliseconds. Default is 3000ms. |

#### Returns

`Promise`\<`WindowInfoResult`\>

WindowInfoResult with active window information and requestId

**`Deprecated`**

Use session.computer.getActiveWindow() instead.

___

### getWindowInfo

▸ **getWindowInfo**(`windowId`): `Promise`\<`WindowInfoResult`\>

Gets information about a specific window.
Corresponds to Python's get_window_info() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | The ID of the window to get information for. |

#### Returns

`Promise`\<`WindowInfoResult`\>

WindowInfoResult with window information and requestId

**`Deprecated`**

Use session.computer.getWindowInfo() instead.

___

### listAllWindows

▸ **listAllWindows**(`timeoutMs?`): `Promise`\<`WindowListResult`\>

Lists all windows in the system.
Corresponds to Python's list_all_windows() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `timeoutMs` | `number` | `3000` | The timeout in milliseconds. Default is 3000ms. |

#### Returns

`Promise`\<`WindowListResult`\>

WindowListResult with windows array and requestId

**`Deprecated`**

Use session.computer.listAllWindows() instead.

___

### listRootWindows

▸ **listRootWindows**(`timeoutMs?`): `Promise`\<`WindowListResult`\>

Lists all root windows in the system.
Corresponds to Python's list_root_windows() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `timeoutMs` | `number` | `3000` | The timeout in milliseconds. Default is 3000ms. |

#### Returns

`Promise`\<`WindowListResult`\>

WindowListResult with windows array and requestId

**`Deprecated`**

Use session.computer.listRootWindows() instead.

___

### maximizeWindow

▸ **maximizeWindow**(`windowId`): `Promise`\<`BoolResult`\>

Maximizes a window.
Corresponds to Python's maximize_window() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | The ID of the window to maximize. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Deprecated`**

Use session.computer.maximizeWindow() instead.

___

### minimizeWindow

▸ **minimizeWindow**(`windowId`): `Promise`\<`BoolResult`\>

Minimizes a window.
Corresponds to Python's minimize_window() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | The ID of the window to minimize. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Deprecated`**

Use session.computer.minimizeWindow() instead.

___

### moveWindow

▸ **moveWindow**(`windowId`, `x`, `y`): `Promise`\<`BoolResult`\>

Moves a window to the specified position.
Corresponds to Python's move_window() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | The ID of the window to move. |
| `x` | `number` | The new x coordinate of the window. |
| `y` | `number` | The new y coordinate of the window. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Deprecated`**

Use session.computer.moveWindow() instead.

___

### resizeWindow

▸ **resizeWindow**(`windowId`, `width`, `height`): `Promise`\<`BoolResult`\>

Resizes a window to the specified dimensions.
Corresponds to Python's resize_window() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `windowId` | `number` | The ID of the window to resize. |
| `width` | `number` | The new width of the window. |
| `height` | `number` | The new height of the window. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Deprecated`**

Use session.computer.resizeWindow() instead.

___

### restoreWindow

▸ **restoreWindow**(`windowId`): `Promise`\<`BoolResult`\>

Restores a window by ID.
Corresponds to Python's restore_window() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :---## Related Resources

- [Computer API Reference](../../computer-use/computer.md)
- [Application API Reference](../../computer-use/application.md)


--- |
| `windowId` | `number` | The ID of the window to restore. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with requestId
