/**
 * Key name normalization utilities for press_keys tool.
 *
 * This module provides utilities to normalize key names to the correct case format
 * expected by the press_keys MCP tool, improving case compatibility.
 */

// Define key name mappings with correct case formats
// Category 1: Modifier keys - should be Title Case
const MODIFIER_KEYS: Record<string, string> = {
  ctrl: "Ctrl",
  control: "Ctrl",
  alt: "Alt",
  shift: "Shift",
  win: "Win",
  windows: "Win",
  meta: "Meta",
  super: "Super",
  command: "Command",
  cmd: "Command",
};

// Category 2: Function keys - should be Title Case
const FUNCTION_KEYS: Record<string, string> = {
  tab: "Tab",
  enter: "Enter",
  return: "Enter",
  escape: "Escape",
  esc: "Escape",
  backspace: "Backspace",
  delete: "Delete",
  del: "Delete",
  insert: "Insert",
  ins: "Insert",
  home: "Home",
  end: "End",
  pageup: "PageUp",
  pagedown: "PageDown",
  pgup: "PageUp",
  pgdn: "PageDown",
  space: "Space",
  capslock: "CapsLock",
  numlock: "NumLock",
  scrolllock: "ScrollLock",
  printscreen: "PrintScreen",
  prtsc: "PrintScreen",
  pause: "Pause",
  break: "Pause",
};

// Category 3: Arrow keys - should be Title Case
const ARROW_KEYS: Record<string, string> = {
  arrowup: "ArrowUp",
  arrowdown: "ArrowDown",
  arrowleft: "ArrowLeft",
  arrowright: "ArrowRight",
  up: "ArrowUp",
  down: "ArrowDown",
  left: "ArrowLeft",
  right: "ArrowRight",
};

// Category 4: Special characters - as-is
const SPECIAL_CHARS: Record<string, string> = {
  minus: "-",
  equal: "=",
  leftbracket: "[",
  rightbracket: "]",
  backslash: "\\",
  semicolon: ";",
  quote: "'",
  comma: ",",
  period: ".",
  slash: "/",
  backtick: "`",
};

// Category 5: F-keys - Title Case (F1, F2, ..., F24)
const F_KEYS: Record<string, string> = {};
for (let i = 1; i <= 24; i++) {
  const fKeyLower = `f${i}`;
  const fKeyUpper = `F${i}`;
  F_KEYS[fKeyLower] = fKeyUpper;
}

/**
 * Normalize a single key name to the correct case format.
 *
 * @param key - The key name to normalize (can be any case)
 * @returns The normalized key name with correct case
 *
 * Rules:
 * - Letter keys (a-z): Convert to lowercase
 * - Number keys (0-9): Keep as-is
 * - Modifier keys: Convert to Title Case (Ctrl, Alt, Shift, Win, etc.)
 * - Function keys: Convert to Title Case (Tab, Enter, Escape, etc.)
 * - Arrow keys: Convert to Title Case (ArrowUp, ArrowDown, etc.)
 * - F-keys: Convert to correct format (F1, F2, ..., F12)
 * - Unknown keys: Return as-is
 *
 * @example
 * ```typescript
 * normalizeSingleKey("A")        // returns "a"
 * normalizeSingleKey("ctrl")     // returns "Ctrl"
 * normalizeSingleKey("CTRL")     // returns "Ctrl"
 * normalizeSingleKey("TAB")      // returns "Tab"
 * normalizeSingleKey("f1")       // returns "F1"
 * ```
 */
function normalizeSingleKey(key: string): string {
  if (!key) {
    return key;
  }

  // Convert to lowercase for comparison
  const keyLower = key.toLowerCase();

  // Check if it's a single letter (a-z)
  if (key.length === 1 && /[a-zA-Z]/.test(key)) {
    return key.toLowerCase();
  }

  // Check if it's a single digit (0-9)
  if (key.length === 1 && /[0-9]/.test(key)) {
    return key;
  }

  // Check modifier keys
  if (keyLower in MODIFIER_KEYS) {
    return MODIFIER_KEYS[keyLower];
  }

  // Check function keys
  if (keyLower in FUNCTION_KEYS) {
    return FUNCTION_KEYS[keyLower];
  }

  // Check arrow keys
  if (keyLower in ARROW_KEYS) {
    return ARROW_KEYS[keyLower];
  }

  // Check F-keys
  if (keyLower in F_KEYS) {
    return F_KEYS[keyLower];
  }

  // Check special characters
  if (keyLower in SPECIAL_CHARS) {
    return SPECIAL_CHARS[keyLower];
  }

  // If the key is already in a known good format (starts with uppercase letter
  // and is not all uppercase), assume it's already correct
  if (
    key[0] === key[0].toUpperCase() &&
    key !== key.toUpperCase() &&
    !["Control", "Windows", "Command"].includes(key)
  ) {
    return key;
  }

  // Unknown key - return as-is
  return key;
}

/**
 * Normalize a list of key names to the correct case format for press_keys tool.
 *
 * This function automatically converts key names to the format expected by the
 * press_keys MCP tool, improving case compatibility and user experience.
 *
 * @param keys - Array of key names to normalize (can be any case)
 * @returns Array of normalized key names with correct case
 *
 * @example
 * ```typescript
 * normalizeKeys(["CTRL", "C"])           // returns ["Ctrl", "c"]
 * normalizeKeys(["ctrl", "shift", "Z"])  // returns ["Ctrl", "Shift", "z"]
 * normalizeKeys(["alt", "TAB"])          // returns ["Alt", "Tab"]
 * normalizeKeys(["win", "d"])            // returns ["Win", "d"]
 * ```
 *
 * Note:
 * - Modifier keys are converted to Title Case (Ctrl, Alt, Shift, Win)
 * - Function keys are converted to Title Case (Tab, Enter, Escape)
 * - Letter keys are converted to lowercase (a, b, c)
 * - Number keys remain unchanged (0, 1, 2)
 * - Unknown keys are returned as-is
 */
export function normalizeKeys(keys: string[]): string[] {
  if (!keys) {
    return keys;
  }

  const normalized: string[] = [];
  for (const key of keys) {
    if (typeof key === "string") {
      normalized.push(normalizeSingleKey(key));
    } else {
      // Non-string keys are passed through unchanged
      normalized.push(key);
    }
  }

  return normalized;
}

/**
 * Get a dictionary of all supported key name mappings.
 *
 * @returns Object with categories and their supported key names
 *
 * @example
 * ```typescript
 * const mappings = getSupportedKeyNames();
 * console.log(mappings.modifierKeys);  // { ctrl: 'Ctrl', alt: 'Alt', ... }
 * ```
 */
export function getSupportedKeyNames(): {
  modifierKeys: Record<string, string>;
  functionKeys: Record<string, string>;
  arrowKeys: Record<string, string>;
  fKeys: Record<string, string>;
  specialChars: Record<string, string>;
} {
  return {
    modifierKeys: MODIFIER_KEYS,
    functionKeys: FUNCTION_KEYS,
    arrowKeys: ARROW_KEYS,
    fKeys: F_KEYS,
    specialChars: SPECIAL_CHARS,
  };
}
