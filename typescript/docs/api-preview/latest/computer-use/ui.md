# Class: UI

## 🎨 Related Tutorial

- [UI Automation Guide](../../../../../../docs/guides/computer-use/computer-ui-automation.md) - Automate UI interactions

Handles UI operations in the AgentBay cloud environment.

**`Deprecated`**

This module is deprecated. Use Computer or Mobile modules instead.
- For desktop UI operations, use session.computer
- For mobile UI operations, use session.mobile

## Table of contents

### Constructors

- [constructor](ui.md#constructor)

### Methods

- [click](ui.md#click)
- [getAllUIElements](ui.md#getalluielements)
- [getClickableUIElements](ui.md#getclickableuielements)
- [inputText](ui.md#inputtext)
- [screenshot](ui.md#screenshot)
- [sendKey](ui.md#sendkey)
- [swipe](ui.md#swipe)

## Constructors

### constructor

• **new UI**(`session`): [`UI`](ui.md)

Initialize a UI object.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `session` | `Object` | The Session instance that this UI belongs to. |
| `session.callMcpTool` | (`toolName`: `string`, `args`: `any`) => `Promise`\<\{ `data`: `string` ; `errorMessage`: `string` ; `requestId`: `string` ; `success`: `boolean`  }\> | - |
| `session.getAPIKey` | () => `string` | - |
| `session.getClient` | () => `any` | - |
| `session.getSessionId` | () => `string` | - |

#### Returns

[`UI`](ui.md)

## Methods

### click

▸ **click**(`x`, `y`, `button?`): `Promise`\<`BoolResult`\>

Clicks on the screen at the specified coordinates.
Corresponds to Python's click() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `x` | `number` | `undefined` | The X coordinate |
| `y` | `number` | `undefined` | The Y coordinate |
| `button` | `string` | `"left"` | The mouse button to use. Default is 'left' |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Throws`**

Error if the operation fails.

**`Deprecated`**

Use session.computer.clickMouse() for desktop or session.mobile.tap() for mobile instead.

___

### getAllUIElements

▸ **getAllUIElements**(`timeoutMs?`): `Promise`\<`UIElementListResult`\>

Retrieves all UI elements regardless of their clickable status.
Corresponds to Python's get_all_ui_elements() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `timeoutMs` | `number` | `2000` | The timeout in milliseconds. Default is 2000ms. |

#### Returns

`Promise`\<`UIElementListResult`\>

UIElementListResult with all elements and requestId

**`Throws`**

Error if the operation fails.

**`Deprecated`**

Use session.computer.getAllUIElements() for desktop or session.mobile.getAllUIElements() for mobile instead.

___

### getClickableUIElements

▸ **getClickableUIElements**(`timeoutMs?`): `Promise`\<`UIElementListResult`\>

Retrieves all clickable UI elements within the specified timeout.
Corresponds to Python's get_clickable_ui_elements() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `timeoutMs` | `number` | `2000` | The timeout in milliseconds. Default is 2000ms. |

#### Returns

`Promise`\<`UIElementListResult`\>

UIElementListResult with clickable elements and requestId

**`Throws`**

Error if the operation fails.

**`Deprecated`**

Use session.computer.getClickableUIElements() for desktop or session.mobile.getClickableUIElements() for mobile instead.

___

### inputText

▸ **inputText**(`text`): `Promise`\<`BoolResult`\>

Inputs text into the currently focused UI element.
Corresponds to Python's input_text() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `text` | `string` | The text to input |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Throws`**

Error if the operation fails.

**`Deprecated`**

Use session.computer.inputText() for desktop or session.mobile.inputText() for mobile instead.

___

### screenshot

▸ **screenshot**(): `Promise`\<`OperationResult`\>

Takes a screenshot of the current screen.
Corresponds to Python's screenshot() method

#### Returns

`Promise`\<`OperationResult`\>

OperationResult with success status and requestId

**`Throws`**

Error if the operation fails.

**`Deprecated`**

Use session.computer.screenshot() for desktop or session.mobile.screenshot() for mobile instead.

___

### sendKey

▸ **sendKey**(`key`): `Promise`\<`BoolResult`\>

Sends a key press event.
Corresponds to Python's send_key() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `key` | `number` | The key code to send. Supported key codes are: - 3 : HOME - 4 : BACK - 24 : VOLUME UP - 25 : VOLUME DOWN - 26 : POWER - 82 : MENU |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Throws`**

Error if the operation fails.

**`Deprecated`**

Use session.computer.pressKeys() for desktop or session.mobile.sendKey() for mobile instead.

___

### swipe

▸ **swipe**(`startX`, `startY`, `endX`, `endY`, `durationMs?`): `Promise`\<`BoolResult`\>

Performs a swipe gesture on the screen.
Corresponds to Python's swipe() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `startX` | `number` | `undefined` | The starting X coordinate |
| `startY` | `number` | `undefined` | The starting Y coordinate |
| `endX` | `number` | `undefined` | The ending X coordinate |
| `endY` | `number` | `undefined` | The ending Y coordinate |
| `durationMs` | `number` | `300` | The duration of the swipe in milliseconds. Default is 300ms. |

#### Returns

`Promise`\<`BoolResult`\>

BoolResult with success status and requestId

**`Throws`**

Error if the operation fails.

**`Deprecated`**

Use session.computer.dragMouse() for desktop or session.mobile.swipe() for mobile instead.

## Related Resources

- [Computer API Reference](computer.md)

