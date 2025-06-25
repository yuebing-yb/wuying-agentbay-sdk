# Window Class

The Window class provides methods for managing windows in the AgentBay cloud environment, including listing windows, getting the active window, and manipulating window states.

## Class Properties

### Python

```python
class Window:
    def __init__(self, session):
        self.session = session
```

### TypeScript

```typescript
class Window {
    private session: Session;

    constructor(session: Session) {
        this.session = session;
    }
}
```

### Golang

```go
type WindowManager struct {
    Session interface {
        GetAPIKey() string
        GetClient() *mcp.Client
        GetSessionId() string
    }
}
```

## Data Types

### Window

Represents a window in the system.

#### Python

```python
class Window:
    window_id: int            # The unique identifier of the window
    title: str                # The title of the window
    absolute_upper_left_x: int # The X coordinate of the upper left corner (optional)
    absolute_upper_left_y: int # The Y coordinate of the upper left corner (optional)
    width: int                # The width of the window (optional)
    height: int               # The height of the window (optional)
    pid: int                  # The process ID of the process that owns the window (optional)
    pname: str                # The name of the process that owns the window (optional)
    child_windows: List[Window] # The child windows of this window (optional)
```

#### TypeScript

```typescript
interface Window {
    window_id: number;         // The unique identifier of the window
    title: string;             // The title of the window
    absolute_upper_left_x?: number; // The X coordinate of the upper left corner (optional)
    absolute_upper_left_y?: number; // The Y coordinate of the upper left corner (optional)
    width?: number;            // The width of the window (optional)
    height?: number;           // The height of the window (optional)
    pid?: number;              // The process ID of the process that owns the window (optional)
    pname?: string;            // The name of the process that owns the window (optional)
    child_windows?: Window[];  // The child windows of this window (optional)
}
```

#### Golang

```go
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
```

## Methods

### list_root_windows / listRootWindows / ListRootWindows

Lists all root windows in the system.

#### Python

```python
def list_root_windows(self) -> List[Window]:
```

**Returns:**
- `List[Window]`: A list of root windows.

**Raises:**
- `WindowError`: If there's an error listing the root windows.

#### TypeScript

```typescript
async listRootWindows(): Promise<Window[]>
```

**Returns:**
- `Promise<Window[]>`: A promise that resolves to a list of root windows.

**Throws:**
- `APIError`: If there's an error listing the root windows.

#### Golang

```go
func (wm *WindowManager) ListRootWindows() (string, error)
```

**Returns:**
- `string`: A JSON string containing the list of root windows.
- `error`: An error if the operation fails.

### get_active_window / getActiveWindow / GetActiveWindow

Gets the currently active window.

#### Python

```python
def get_active_window(self) -> Window:
```

**Returns:**
- `Window`: The currently active window.

**Raises:**
- `WindowError`: If there's an error getting the active window.

#### TypeScript

```typescript
async getActiveWindow(): Promise<Window>
```

**Returns:**
- `Promise<Window>`: A promise that resolves to the currently active window.

**Throws:**
- `APIError`: If there's an error getting the active window.

#### Golang

```go
func (wm *WindowManager) GetActiveWindow() (string, error)
```

**Returns:**
- `string`: A JSON string containing the active window.
- `error`: An error if the operation fails.

### activate_window / activateWindow / ActivateWindow

Activates (brings to front) a window by ID.

#### Python

```python
def activate_window(self, window_id: int) -> bool:
```

**Parameters:**
- `window_id` (int): The ID of the window to activate.

**Returns:**
- `bool`: True if the operation was successful, False otherwise.

**Raises:**
- `WindowError`: If there's an error activating the window.

#### TypeScript

```typescript
async activateWindow(windowId: number): Promise<boolean>
```

**Parameters:**
- `windowId` (number): The ID of the window to activate.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the operation was successful, false otherwise.

**Throws:**
- `APIError`: If there's an error activating the window.

#### Golang

```go
func (wm *WindowManager) ActivateWindow(windowID int) error
```

**Parameters:**
- `windowID` (int): The ID of the window to activate.

**Returns:**
- `error`: An error if the operation fails.

### minimize_window / minimizeWindow / MinimizeWindow

Minimizes a window by ID.

#### Python

```python
def minimize_window(self, window_id: int) -> bool:
```

**Parameters:**
- `window_id` (int): The ID of the window to minimize.

**Returns:**
- `bool`: True if the operation was successful, False otherwise.

**Raises:**
- `WindowError`: If there's an error minimizing the window.

#### TypeScript

```typescript
async minimizeWindow(windowId: number): Promise<boolean>
```

**Parameters:**
- `windowId` (number): The ID of the window to minimize.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the operation was successful, false otherwise.

**Throws:**
- `APIError`: If there's an error minimizing the window.

#### Golang

```go
func (wm *WindowManager) MinimizeWindow(windowID int) error
```

**Parameters:**
- `windowID` (int): The ID of the window to minimize.

**Returns:**
- `error`: An error if the operation fails.

### maximize_window / maximizeWindow / MaximizeWindow

Maximizes a window by ID.

#### Python

```python
def maximize_window(self, window_id: int) -> bool:
```

**Parameters:**
- `window_id` (int): The ID of the window to maximize.

**Returns:**
- `bool`: True if the operation was successful, False otherwise.

**Raises:**
- `WindowError`: If there's an error maximizing the window.

#### TypeScript

```typescript
async maximizeWindow(windowId: number): Promise<boolean>
```

**Parameters:**
- `windowId` (number): The ID of the window to maximize.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the operation was successful, false otherwise.

**Throws:**
- `APIError`: If there's an error maximizing the window.

#### Golang

```go
func (wm *WindowManager) MaximizeWindow(windowID int) error
```

**Parameters:**
- `windowID` (int): The ID of the window to maximize.

**Returns:**
- `error`: An error if the operation fails.

### restore_window / restoreWindow / RestoreWindow

Restores a window by ID (from minimized or maximized state).

#### Python

```python
def restore_window(self, window_id: int) -> bool:
```

**Parameters:**
- `window_id` (int): The ID of the window to restore.

**Returns:**
- `bool`: True if the operation was successful, False otherwise.

**Raises:**
- `WindowError`: If there's an error restoring the window.

#### TypeScript

```typescript
async restoreWindow(windowId: number): Promise<boolean>
```

**Parameters:**
- `windowId` (number): The ID of the window to restore.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the operation was successful, false otherwise.

**Throws:**
- `APIError`: If there's an error restoring the window.

#### Golang

```go
func (wm *WindowManager) RestoreWindow(windowID int) error
```

**Parameters:**
- `windowID` (int): The ID of the window to restore.

**Returns:**
- `error`: An error if the operation fails.

### fullscreen_window / fullscreenWindow / FullscreenWindow

Makes a window fullscreen by ID.

#### Python

```python
def fullscreen_window(self, window_id: int) -> bool:
```

**Parameters:**
- `window_id` (int): The ID of the window to make fullscreen.

**Returns:**
- `bool`: True if the operation was successful, False otherwise.

**Raises:**
- `WindowError`: If there's an error making the window fullscreen.

#### TypeScript

```typescript
async fullscreenWindow(windowId: number): Promise<boolean>
```

**Parameters:**
- `windowId` (number): The ID of the window to make fullscreen.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the operation was successful, false otherwise.

**Throws:**
- `APIError`: If there's an error making the window fullscreen.

#### Golang

```go
func (wm *WindowManager) FullscreenWindow(windowID int) error
```

**Parameters:**
- `windowID` (int): The ID of the window to make fullscreen.

**Returns:**
- `error`: An error if the operation fails.

### resize_window / resizeWindow / ResizeWindow

Resizes a window by ID to the specified width and height.

#### Python

```python
def resize_window(self, window_id: int, width: int, height: int) -> bool:
```

**Parameters:**
- `window_id` (int): The ID of the window to resize.
- `width` (int): The new width of the window.
- `height` (int): The new height of the window.

**Returns:**
- `bool`: True if the operation was successful, False otherwise.

**Raises:**
- `WindowError`: If there's an error resizing the window.

#### TypeScript

```typescript
async resizeWindow(windowId: number, width: number, height: number): Promise<boolean>
```

**Parameters:**
- `windowId` (number): The ID of the window to resize.
- `width` (number): The new width of the window.
- `height` (number): The new height of the window.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the operation was successful, false otherwise.

**Throws:**
- `APIError`: If there's an error resizing the window.

#### Golang

```go
func (wm *WindowManager) ResizeWindow(windowID, width, height int) error
```

**Parameters:**
- `windowID` (int): The ID of the window to resize.
- `width` (int): The new width of the window.
- `height` (int): The new height of the window.

**Returns:**
- `error`: An error if the operation fails.

### close_window / closeWindow / CloseWindow

Closes a window by ID.

#### Python

```python
def close_window(self, window_id: int) -> bool:
```

**Parameters:**
- `window_id` (int): The ID of the window to close.

**Returns:**
- `bool`: True if the operation was successful, False otherwise.

**Raises:**
- `WindowError`: If there's an error closing the window.

#### TypeScript

```typescript
async closeWindow(windowId: number): Promise<boolean>
```

**Parameters:**
- `windowId` (number): The ID of the window to close.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the operation was successful, false otherwise.

**Throws:**
- `APIError`: If there's an error closing the window.

#### Golang

```go
func (wm *WindowManager) CloseWindow(windowID int) error
```

**Parameters:**
- `windowID` (int): The ID of the window to close.

**Returns:**
- `error`: An error if the operation fails.

### focus_mode / focusMode / FocusMode

Enables or disables focus mode, which prevents window switching.

#### Python

```python
def focus_mode(self, on: bool) -> bool:
```

**Parameters:**
- `on` (bool): True to enable focus mode, False to disable it.

**Returns:**
- `bool`: True if the operation was successful, False otherwise.

**Raises:**
- `WindowError`: If there's an error setting focus mode.

#### TypeScript

```typescript
async focusMode(on: boolean): Promise<boolean>
```

**Parameters:**
- `on` (boolean): True to enable focus mode, False to disable it.

**Returns:**
- `Promise<boolean>`: A promise that resolves to true if the operation was successful, false otherwise.

**Throws:**
- `APIError`: If there's an error setting focus mode.

#### Golang

```go
func (wm *WindowManager) FocusMode(on bool) error
```

**Parameters:**
- `on` (bool): True to enable focus mode, False to disable it.

**Returns:**
- `error`: An error if the operation fails.

## Usage Examples

### Python

```python
# Create a session
session = agent_bay.create()

# List root windows
root_windows = session.window.list_root_windows()
for window in root_windows:
    print(f"Window: {window.title} (ID: {window.window_id}, Process: {window.pname}, PID: {window.pid})")

# Get active window
active_window = session.window.get_active_window()
print(f"Active window: {active_window.title} (ID: {active_window.window_id})")

# Manipulate windows
if root_windows:
    window_id = root_windows[0].window_id
    
    # Maximize window
    session.window.maximize_window(window_id)
    print("Window maximized")
    
    # Restore window
    session.window.restore_window(window_id)
    print("Window restored")
    
    # Resize window
    session.window.resize_window(window_id, 800, 600)
    print("Window resized")
    
    # Activate window
    session.window.activate_window(window_id)
    print("Window activated")
```

### TypeScript

```typescript
// Create a session
const session = await agentBay.create();

// List root windows
const rootWindows = await session.window.listRootWindows();
for (const window of rootWindows) {
  console.log(`Window: ${window.title} (ID: ${window.window_id}, Process: ${window.pname}, PID: ${window.pid})`);
}

// Get active window
const activeWindow = await session.window.getActiveWindow();
console.log(`Active window: ${activeWindow.title} (ID: ${activeWindow.window_id})`);

// Manipulate windows
if (rootWindows.length > 0) {
  const windowId = rootWindows[0].window_id;
  
  // Maximize window
  await session.window.maximizeWindow(windowId);
  console.log("Window maximized");
  
  // Restore window
  await session.window.restoreWindow(windowId);
  console.log("Window restored");
  
  // Resize window
  await session.window.resizeWindow(windowId, 800, 600);
  console.log("Window resized");
  
  // Activate window
  await session.window.activateWindow(windowId);
  console.log("Window activated");
}
```

### Golang

```go
// Create a session
session, err := client.Create(nil)
if err != nil {
    // Handle error
}

// List root windows
rootWindowsJSON, err := session.Window.ListRootWindows()
if err != nil {
    // Handle error
}

var rootWindows []Window
if err := json.Unmarshal([]byte(rootWindowsJSON), &rootWindows); err != nil {
    // Handle error
}
for _, window := range rootWindows {
    fmt.Printf("Window: %s (ID: %d, Process: %s, PID: %d)\n", 
               window.Title, window.WindowID, window.PName, window.PID)
}

// Get active window
activeWindowJSON, err := session.Window.GetActiveWindow()
if err != nil {
    // Handle error
}

var activeWindow Window
if err := json.Unmarshal([]byte(activeWindowJSON), &activeWindow); err != nil {
    // Handle error
}
fmt.Printf("Active window: %s (ID: %d)\n", activeWindow.Title, activeWindow.WindowID)

// Manipulate windows
if len(rootWindows) > 0 {
    windowID := rootWindows[0].WindowID
    
    // Maximize window
    err = session.Window.MaximizeWindow(windowID)
    if err != nil {
        // Handle error
    }
    fmt.Println("Window maximized")
    
    // Restore window
    err = session.Window.RestoreWindow(windowID)
    if err != nil {
        // Handle error
    }
    fmt.Println("Window restored")
    
    // Resize window
    err = session.Window.ResizeWindow(windowID, 800, 600)
    if err != nil {
        // Handle error
    }
    fmt.Println("Window resized")
    
    // Activate window
    err = session.Window.ActivateWindow(windowID)
    if err != nil {
        // Handle error
    }
    fmt.Println("Window activated")
}
```

## Related Resources

- [Session Class](session.md): The session class that provides access to the Window class.
- [Application Class](application.md): The application class for managing applications in the cloud environment.
- [Applications Concept](../concepts/applications.md): Conceptual information about applications and windows in the AgentBay cloud environment. 