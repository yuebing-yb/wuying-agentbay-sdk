# UI Class API Reference

The `UI` class provides methods for interacting with UI elements in the AgentBay cloud environment. This includes retrieving UI elements, sending key events, inputting text, performing gestures, and taking screenshots.

## Properties

### Python

- `KeyCode`: Constants for key codes that can be used with the `send_key` method.
  - `HOME`: Home key (3)
  - `BACK`: Back key (4)
  - `VOLUME_UP`: Volume up key (24)
  - `VOLUME_DOWN`: Volume down key (25)
  - `POWER`: Power key (26)
  - `MENU`: Menu key (82)

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

#### Python

```python
get_clickable_ui_elements(timeout_ms: int = 2000) -> List[Dict[str, Any]]
```

**Parameters:**
- `timeout_ms` (int, optional): The timeout in milliseconds. Default is 2000ms.

**Returns:**
- `List[Dict[str, Any]]`: A list of clickable UI elements.

**Raises:**
- `AgentBayError`: If the operation fails.

#### TypeScript

```typescript
getClickableUIElements(timeoutMs?: number): Promise<string>
```

**Parameters:**
- `timeoutMs` (number, optional): The timeout in milliseconds. Default is 2000ms.

**Returns:**
- `Promise<string>`: A promise that resolves to a string representation of clickable UI elements.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
GetClickableUIElements(timeoutMs int) (string, error)
```

**Parameters:**
- `timeoutMs` (int): The timeout in milliseconds. If <= 0, default is 2000ms.

**Returns:**
- `string`: String representation of clickable UI elements.
- `error`: An error if the operation fails.

### get_all_ui_elements / getAllUIElements / GetAllUIElements

Retrieves all UI elements within the specified timeout.

#### Python

```python
get_all_ui_elements(timeout_ms: int = 2000) -> List[Dict[str, Any]]
```

**Parameters:**
- `timeout_ms` (int, optional): The timeout in milliseconds. Default is 2000ms.

**Returns:**
- `List[Dict[str, Any]]`: A list of all UI elements with parsed details.

**Raises:**
- `AgentBayError`: If the operation fails.

#### TypeScript

```typescript
getAllUIElements(timeoutMs?: number): Promise<string>
```

**Parameters:**
- `timeoutMs` (number, optional): The timeout in milliseconds. Default is 2000ms.

**Returns:**
- `Promise<string>`: A promise that resolves to a string representation of all UI elements.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
GetAllUIElements(timeoutMs int) (string, error)
```

**Parameters:**
- `timeoutMs` (int): The timeout in milliseconds. If <= 0, default is 2000ms.

**Returns:**
- `string`: String representation of all UI elements.
- `error`: An error if the operation fails.

### send_key / sendKey / SendKey

Sends a key press event.

#### Python

```python
send_key(key: int) -> bool
```

**Parameters:**
- `key` (int): The key code to send. Use the `KeyCode` constants.

**Returns:**
- `bool`: True if the key press was successful.

**Raises:**
- `AgentBayError`: If the operation fails.

#### TypeScript

```typescript
sendKey(key: number): Promise<string>
```

**Parameters:**
- `key` (number): The key code to send. Use the `KeyCode` constants.

**Returns:**
- `Promise<string>`: A promise that resolves to the response text.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
SendKey(key int) (string, error)
```

**Parameters:**
- `key` (int): The key code to send. Use the `KeyCode` constants.

**Returns:**
- `string`: The response text.
- `error`: An error if the operation fails.

### input_text / inputText / InputText

Inputs text into the active field.

#### Python

```python
input_text(text: str) -> None
```

**Parameters:**
- `text` (string): The text to input.

**Raises:**
- `AgentBayError`: If the operation fails.

#### TypeScript

```typescript
inputText(text: string): Promise<string>
```

**Parameters:**
- `text` (string): The text to input.

**Returns:**
- `Promise<string>`: A promise that resolves to the response text.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
InputText(text string) (string, error)
```

**Parameters:**
- `text` (string): The text to input.

**Returns:**
- `string`: The response text.
- `error`: An error if the operation fails.

### swipe / Swipe

Performs a swipe gesture on the screen.

#### Python

```python
swipe(start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 300) -> None
```

**Parameters:**
- `start_x` (int): The starting X coordinate.
- `start_y` (int): The starting Y coordinate.
- `end_x` (int): The ending X coordinate.
- `end_y` (int): The ending Y coordinate.
- `duration_ms` (int, optional): The duration of the swipe in milliseconds. Default is 300ms.

**Raises:**
- `AgentBayError`: If the operation fails.

#### TypeScript

```typescript
swipe(startX: number, startY: number, endX: number, endY: number, durationMs?: number): Promise<string>
```

**Parameters:**
- `startX` (number): The starting X coordinate.
- `startY` (number): The starting Y coordinate.
- `endX` (number): The ending X coordinate.
- `endY` (number): The ending Y coordinate.
- `durationMs` (number, optional): The duration of the swipe in milliseconds. Default is 300ms.

**Returns:**
- `Promise<string>`: A promise that resolves to the response text.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
Swipe(startX, startY, endX, endY, durationMs int) (string, error)
```

**Parameters:**
- `startX` (int): The starting X coordinate.
- `startY` (int): The starting Y coordinate.
- `endX` (int): The ending X coordinate.
- `endY` (int): The ending Y coordinate.
- `durationMs` (int): The duration of the swipe in milliseconds. If <= 0, default is 300ms.

**Returns:**
- `string`: The response text.
- `error`: An error if the operation fails.

### click / Click

Clicks on the screen at the specified coordinates.

#### Python

```python
click(x: int, y: int, button: str = "left") -> None
```

**Parameters:**
- `x` (int): The X coordinate.
- `y` (int): The Y coordinate.
- `button` (str, optional): The mouse button to use. Default is 'left'.

**Raises:**
- `AgentBayError`: If the operation fails.

#### TypeScript

```typescript
click(x: number, y: number, button?: string): Promise<string>
```

**Parameters:**
- `x` (number): The X coordinate.
- `y` (number): The Y coordinate.
- `button` (string, optional): The mouse button to use. Default is 'left'.

**Returns:**
- `Promise<string>`: A promise that resolves to the response text.

**Throws:**
- `APIError`: If the operation fails.

#### Golang

```go
Click(x, y int, button string) (string, error)
```

**Parameters:**
- `x` (int): The X coordinate.
- `y` (int): The Y coordinate.
- `button` (string): The mouse button to use. If empty, default is 'left'.

**Returns:**
- `string`: The response text.
- `error`: An error if the operation fails.

### screenshot / Screenshot

Takes a screenshot of the current screen.

#### Python

```python
screenshot() -> str
```

**Returns:**
- `str`: The screenshot data.

**Raises:**
- `AgentBayError`: If the operation fails.

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

### Python

```python
# Take a screenshot
screenshot = session.ui.screenshot()
print(f"Screenshot data length: {len(screenshot)} characters")

# Get all UI elements
elements = session.ui.get_all_ui_elements()
print(f"Retrieved {len(elements)} UI elements")

# Get clickable UI elements
clickable_elements = session.ui.get_clickable_ui_elements()
print(f"Retrieved {len(clickable_elements)} clickable UI elements")

# Send a key press
result = session.ui.send_key(KeyCode.HOME)
print(f"Send key result: {result}")

# Input text
session.ui.input_text("Hello, world!")

# Perform a swipe gesture
session.ui.swipe(100, 500, 100, 100, 500)

# Click on the screen
session.ui.click(200, 300)
```

### TypeScript

```typescript
// Take a screenshot
const screenshot = await session.ui.screenshot();
log(`Screenshot data length: ${screenshot.length} characters`);

// Get all UI elements
const elements = await session.ui.getAllUIElements();
log(`Retrieved UI elements: ${elements}`);

// Get clickable UI elements
const clickableElements = await session.ui.getClickableUIElements();
log(`Retrieved clickable UI elements: ${clickableElements}`);

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
fmt.Printf("Retrieved UI elements: %s\n", elements)

// Get clickable UI elements
clickableElements, err := session.UI.GetClickableUIElements(2000)
if err != nil {
    // Handle error
}
fmt.Printf("Retrieved clickable UI elements: %s\n", clickableElements)

// Send a key press
result, err := session.UI.SendKey(KeyCode.HOME)
if err != nil {
    // Handle error
}
fmt.Printf("Send key result: %s\n", result)

// Input text
response, err := session.UI.InputText("Hello, world!")
if err != nil {
    // Handle error
}

// Perform a swipe gesture
response, err = session.UI.Swipe(100, 500, 100, 100, 500)
if err != nil {
    // Handle error
}

// Click on the screen
response, err = session.UI.Click(200, 300, "left")
if err != nil {
    // Handle error
}
```

## Related Resources

- [Session Class](session.md): The Session class that provides access to the UI class.
