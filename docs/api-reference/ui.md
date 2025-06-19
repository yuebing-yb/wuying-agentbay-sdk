# UI Class API Reference

The `UI` class provides methods for interacting with UI elements in the AgentBay cloud environment. This includes retrieving UI elements, sending key events, inputting text, performing gestures, and taking screenshots.

## Properties

### TypeScript

- `KeyCode`: Constants for key codes that can be used with the `sendKey` method.
  - `HOME`: Home key (3)
  - `BACK`: Back key (4)
  - `VOLUME_UP`: Volume up key (24)
  - `VOLUME_DOWN`: Volume down key (25)
  - `POWER`: Power key (26)
  - `MENU`: Menu key (82)

### Golang

- `KeyCode`: Constants for key codes that can be used with the `SendKey` method.
  - `HOME`: Home key (3)
  - `BACK`: Back key (4)
  - `VOLUME_UP`: Volume up key (24)
  - `VOLUME_DOWN`: Volume down key (25)
  - `POWER`: Power key (26)
  - `MENU`: Menu key (82)

## Methods

### get_clickable_ui_elements / getClickableUIElements / GetClickableUIElements

Retrieves all clickable UI elements within the specified timeout.

#### TypeScript

```typescript
getClickableUIElements(timeoutMs?: number): Promise<any[]>
```

**Parameters:**
- `timeoutMs` (number, optional): The timeout in milliseconds. Default is 2000ms.

**Returns:**
- `Promise<any[]>`: A promise that resolves to an array of clickable UI elements.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
GetClickableUIElements(timeoutMs int) ([]map[string]interface{}, error)
```

**Parameters:**
- `timeoutMs` (int): The timeout in milliseconds. If <= 0, default is 2000ms.

**Returns:**
- `[]map[string]interface{}`: An array of clickable UI elements.
- `error`: An error if the operation fails.

### get_all_ui_elements / getAllUIElements / GetAllUIElements

Retrieves all UI elements within the specified timeout.

#### TypeScript

```typescript
getAllUIElements(timeoutMs?: number): Promise<any[]>
```

**Parameters:**
- `timeoutMs` (number, optional): The timeout in milliseconds. Default is 2000ms.

**Returns:**
- `Promise<any[]>`: A promise that resolves to an array of UI elements.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
GetAllUIElements(timeoutMs int) ([]map[string]interface{}, error)
```

**Parameters:**
- `timeoutMs` (int): The timeout in milliseconds. If <= 0, default is 2000ms.

**Returns:**
- `[]map[string]interface{}`: An array of UI elements.
- `error`: An error if the operation fails.

### send_key / sendKey / SendKey

Sends a key press event.

#### TypeScript

```typescript
sendKey(key: number): Promise<boolean>
```

**Parameters:**
- `key` (number): The key code to send. Use the `KeyCode` constants.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the key press was successful.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
SendKey(key int) (bool, error)
```

**Parameters:**
- `key` (int): The key code to send. Use the `KeyCode` constants.

**Returns:**
- `bool`: True if the key press was successful.
- `error`: An error if the operation fails.

### input_text / inputText / InputText

Inputs text into the active field.

#### TypeScript

```typescript
inputText(text: string): Promise<void>
```

**Parameters:**
- `text` (string): The text to input.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
InputText(text string) error
```

**Parameters:**
- `text` (string): The text to input.

**Returns:**
- `error`: An error if the operation fails.

### swipe / Swipe

Performs a swipe gesture on the screen.

#### TypeScript

```typescript
swipe(startX: number, startY: number, endX: number, endY: number, durationMs?: number): Promise<void>
```

**Parameters:**
- `startX` (number): The starting X coordinate.
- `startY` (number): The starting Y coordinate.
- `endX` (number): The ending X coordinate.
- `endY` (number): The ending Y coordinate.
- `durationMs` (number, optional): The duration of the swipe in milliseconds. Default is 300ms.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
Swipe(startX, startY, endX, endY, durationMs int) error
```

**Parameters:**
- `startX` (int): The starting X coordinate.
- `startY` (int): The starting Y coordinate.
- `endX` (int): The ending X coordinate.
- `endY` (int): The ending Y coordinate.
- `durationMs` (int): The duration of the swipe in milliseconds. If <= 0, default is 300ms.

**Returns:**
- `error`: An error if the operation fails.

### click / Click

Clicks on the screen at the specified coordinates.

#### TypeScript

```typescript
click(x: number, y: number, button?: string): Promise<void>
```

**Parameters:**
- `x` (number): The X coordinate.
- `y` (number): The Y coordinate.
- `button` (string, optional): The mouse button to use. Default is 'left'.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
Click(x, y int, button string) error
```

**Parameters:**
- `x` (int): The X coordinate.
- `y` (int): The Y coordinate.
- `button` (string): The mouse button to use. If empty, default is 'left'.

**Returns:**
- `error`: An error if the operation fails.

### screenshot / Screenshot

Takes a screenshot of the current screen.

#### TypeScript

```typescript
screenshot(): Promise<string>
```

**Returns:**
- `Promise<string>`: A promise that resolves to the screenshot data.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
Screenshot() (string, error)
```

**Returns:**
- `string`: The screenshot data.
- `error`: An error if the operation fails.

## UI Element Structure

UI elements returned by `getClickableUIElements` and `getAllUIElements` have the following structure:

```typescript
interface UIElement {
  bounds: string;
  className: string;
  text: string;
  type: string;
  resourceId: string;
  index: number;
  isParent: boolean;
  children: UIElement[];
}
```

## Usage Examples

### TypeScript

```typescript
// Take a screenshot
const screenshot = await session.ui.screenshot();
log(`Screenshot data length: ${screenshot.length} characters`);

// Get all UI elements
const elements = await session.ui.getAllUIElements();
log(`Retrieved ${elements.length} UI elements`);

// Get clickable UI elements
const clickableElements = await session.ui.getClickableUIElements();
log(`Retrieved ${clickableElements.length} clickable UI elements`);

// Send a key press
const result = await session.ui.sendKey(KeyCode.HOME);
log(`Send key result: ${result}`);

// Input text
await session.ui.inputText("Hello, world!");

// Perform a swipe gesture
await session.ui.swipe(100, 500, 100, 100, 500);

// Click on the screen
await session.ui.click(200, 300);
```

### Golang

```go
// Take a screenshot
screenshot, err := session.UI.Screenshot()
if err != nil {
    // Handle error
}
fmt.Printf("Screenshot data length: %d characters\n", len(screenshot))

// Get all UI elements
elements, err := session.UI.GetAllUIElements(2000)
if err != nil {
    // Handle error
}
fmt.Printf("Retrieved %d UI elements\n", len(elements))

// Get clickable UI elements
clickableElements, err := session.UI.GetClickableUIElements(2000)
if err != nil {
    // Handle error
}
fmt.Printf("Retrieved %d clickable UI elements\n", len(clickableElements))

// Send a key press
result, err := session.UI.SendKey(ui.KeyCode.HOME)
if err != nil {
    // Handle error
}
fmt.Printf("Send key result: %v\n", result)

// Input text
err = session.UI.InputText("Hello, world!")
if err != nil {
    // Handle error
}

// Perform a swipe gesture
err = session.UI.Swipe(100, 500, 100, 100, 500)
if err != nil {
    // Handle error
}

// Click on the screen
err = session.UI.Click(200, 300, "left")
if err != nil {
    // Handle error
}
```

## Related Resources

- [Session Class](session.md): The Session class that provides access to the UI class.
