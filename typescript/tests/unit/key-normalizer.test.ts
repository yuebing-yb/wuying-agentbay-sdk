import { describe, test, expect } from "@jest/globals";
import { normalizeKeys, getSupportedKeyNames } from "../../src/key-normalizer";

describe("NormalizeSingleKey", () => {
  describe("Letter Keys", () => {
    test("should keep lowercase letters lowercase", () => {
      expect(normalizeKeys(["a"])[0]).toBe("a");
      expect(normalizeKeys(["z"])[0]).toBe("z");
    });

    test("should convert uppercase letters to lowercase", () => {
      expect(normalizeKeys(["A"])[0]).toBe("a");
      expect(normalizeKeys(["Z"])[0]).toBe("z");
    });
  });

  describe("Number Keys", () => {
    test("should keep number keys as-is", () => {
      expect(normalizeKeys(["0"])[0]).toBe("0");
      expect(normalizeKeys(["1"])[0]).toBe("1");
      expect(normalizeKeys(["9"])[0]).toBe("9");
    });
  });

  describe("Modifier Keys", () => {
    test("should normalize ctrl variants", () => {
      expect(normalizeKeys(["ctrl"])[0]).toBe("Ctrl");
      expect(normalizeKeys(["CTRL"])[0]).toBe("Ctrl");
      expect(normalizeKeys(["Ctrl"])[0]).toBe("Ctrl");
      expect(normalizeKeys(["control"])[0]).toBe("Ctrl");
    });

    test("should normalize alt variants", () => {
      expect(normalizeKeys(["alt"])[0]).toBe("Alt");
      expect(normalizeKeys(["ALT"])[0]).toBe("Alt");
      expect(normalizeKeys(["Alt"])[0]).toBe("Alt");
    });

    test("should normalize shift variants", () => {
      expect(normalizeKeys(["shift"])[0]).toBe("Shift");
      expect(normalizeKeys(["SHIFT"])[0]).toBe("Shift");
      expect(normalizeKeys(["Shift"])[0]).toBe("Shift");
    });

    test("should normalize win/windows variants", () => {
      expect(normalizeKeys(["win"])[0]).toBe("Win");
      expect(normalizeKeys(["WIN"])[0]).toBe("Win");
      expect(normalizeKeys(["windows"])[0]).toBe("Win");
      expect(normalizeKeys(["Windows"])[0]).toBe("Win");
    });

    test("should normalize command variants", () => {
      expect(normalizeKeys(["command"])[0]).toBe("Command");
      expect(normalizeKeys(["cmd"])[0]).toBe("Command");
    });

    test("should normalize meta and super", () => {
      expect(normalizeKeys(["meta"])[0]).toBe("Meta");
      expect(normalizeKeys(["super"])[0]).toBe("Super");
    });
  });

  describe("Function Keys", () => {
    test("should normalize tab variants", () => {
      expect(normalizeKeys(["tab"])[0]).toBe("Tab");
      expect(normalizeKeys(["TAB"])[0]).toBe("Tab");
      expect(normalizeKeys(["Tab"])[0]).toBe("Tab");
    });

    test("should normalize enter variants", () => {
      expect(normalizeKeys(["enter"])[0]).toBe("Enter");
      expect(normalizeKeys(["ENTER"])[0]).toBe("Enter");
      expect(normalizeKeys(["return"])[0]).toBe("Enter");
    });

    test("should normalize escape variants", () => {
      expect(normalizeKeys(["escape"])[0]).toBe("Escape");
      expect(normalizeKeys(["ESC"])[0]).toBe("Escape");
      expect(normalizeKeys(["esc"])[0]).toBe("Escape");
    });

    test("should normalize delete variants", () => {
      expect(normalizeKeys(["delete"])[0]).toBe("Delete");
      expect(normalizeKeys(["del"])[0]).toBe("Delete");
    });

    test("should normalize other function keys", () => {
      expect(normalizeKeys(["backspace"])[0]).toBe("Backspace");
      expect(normalizeKeys(["insert"])[0]).toBe("Insert");
      expect(normalizeKeys(["ins"])[0]).toBe("Insert");
      expect(normalizeKeys(["home"])[0]).toBe("Home");
      expect(normalizeKeys(["end"])[0]).toBe("End");
      expect(normalizeKeys(["pageup"])[0]).toBe("PageUp");
      expect(normalizeKeys(["pagedown"])[0]).toBe("PageDown");
      expect(normalizeKeys(["space"])[0]).toBe("Space");
    });
  });

  describe("F-Keys", () => {
    test("should normalize F-keys", () => {
      expect(normalizeKeys(["f1"])[0]).toBe("F1");
      expect(normalizeKeys(["F1"])[0]).toBe("F1");
      expect(normalizeKeys(["f12"])[0]).toBe("F12");
      expect(normalizeKeys(["f24"])[0]).toBe("F24");
    });
  });

  describe("Arrow Keys", () => {
    test("should normalize arrow keys with full names", () => {
      expect(normalizeKeys(["arrowup"])[0]).toBe("ArrowUp");
      expect(normalizeKeys(["ARROWUP"])[0]).toBe("ArrowUp");
      expect(normalizeKeys(["arrowdown"])[0]).toBe("ArrowDown");
      expect(normalizeKeys(["arrowleft"])[0]).toBe("ArrowLeft");
      expect(normalizeKeys(["arrowright"])[0]).toBe("ArrowRight");
    });

    test("should normalize arrow keys with short names", () => {
      expect(normalizeKeys(["up"])[0]).toBe("ArrowUp");
      expect(normalizeKeys(["down"])[0]).toBe("ArrowDown");
      expect(normalizeKeys(["left"])[0]).toBe("ArrowLeft");
      expect(normalizeKeys(["right"])[0]).toBe("ArrowRight");
    });
  });
});

describe("NormalizeKeys", () => {
  describe("Empty Input", () => {
    test("should handle empty array", () => {
      expect(normalizeKeys([])).toEqual([]);
    });

    test("should handle null input", () => {
      expect(normalizeKeys(null as any)).toBe(null);
    });
  });

  describe("Single Key", () => {
    test("should normalize single key", () => {
      expect(normalizeKeys(["a"])).toEqual(["a"]);
      expect(normalizeKeys(["A"])).toEqual(["a"]);
    });
  });

  describe("Modifier Combinations", () => {
    test("should normalize ctrl+c (lowercase)", () => {
      expect(normalizeKeys(["ctrl", "c"])).toEqual(["Ctrl", "c"]);
    });

    test("should normalize CTRL+C (uppercase)", () => {
      expect(normalizeKeys(["CTRL", "C"])).toEqual(["Ctrl", "c"]);
    });

    test("should normalize ctrl+shift+z", () => {
      expect(normalizeKeys(["ctrl", "shift", "z"])).toEqual(["Ctrl", "Shift", "z"]);
    });

    test("should normalize alt+tab", () => {
      expect(normalizeKeys(["alt", "tab"])).toEqual(["Alt", "Tab"]);
    });

    test("should normalize win+d", () => {
      expect(normalizeKeys(["win", "d"])).toEqual(["Win", "d"]);
    });
  });

  describe("Mixed Case", () => {
    test("should normalize CTRL+a", () => {
      expect(normalizeKeys(["CTRL", "a"])).toEqual(["Ctrl", "a"]);
    });

    test("should normalize alt+TAB", () => {
      expect(normalizeKeys(["alt", "TAB"])).toEqual(["Alt", "Tab"]);
    });

    test("should normalize ALT+tab", () => {
      expect(normalizeKeys(["ALT", "tab"])).toEqual(["Alt", "Tab"]);
    });
  });

  describe("F-Keys Combinations", () => {
    test("should normalize alt+f4", () => {
      expect(normalizeKeys(["alt", "f4"])).toEqual(["Alt", "F4"]);
    });

    test("should normalize ALT+F4", () => {
      expect(normalizeKeys(["ALT", "F4"])).toEqual(["Alt", "F4"]);
    });
  });

  describe("Arrow Keys Combinations", () => {
    test("should normalize shift+arrowleft", () => {
      expect(normalizeKeys(["shift", "arrowleft"])).toEqual(["Shift", "ArrowLeft"]);
    });

    test("should normalize SHIFT+LEFT", () => {
      expect(normalizeKeys(["SHIFT", "LEFT"])).toEqual(["Shift", "ArrowLeft"]);
    });
  });

  describe("Key Aliases", () => {
    test("should normalize control to Ctrl", () => {
      expect(normalizeKeys(["control", "c"])).toEqual(["Ctrl", "c"]);
    });

    test("should normalize windows to Win", () => {
      expect(normalizeKeys(["windows", "e"])).toEqual(["Win", "e"]);
    });

    test("should normalize esc to Escape", () => {
      expect(normalizeKeys(["esc"])).toEqual(["Escape"]);
    });

    test("should normalize return to Enter", () => {
      expect(normalizeKeys(["return"])).toEqual(["Enter"]);
    });

    test("should normalize del to Delete", () => {
      expect(normalizeKeys(["del"])).toEqual(["Delete"]);
    });
  });

  describe("Real-World Use Cases", () => {
    test("should normalize common shortcuts", () => {
      // Copy (Ctrl+C)
      expect(normalizeKeys(["ctrl", "c"])).toEqual(["Ctrl", "c"]);

      // Paste (Ctrl+V)
      expect(normalizeKeys(["CTRL", "V"])).toEqual(["Ctrl", "v"]);

      // Undo (Ctrl+Z)
      expect(normalizeKeys(["ctrl", "z"])).toEqual(["Ctrl", "z"]);

      // Redo (Ctrl+Shift+Z)
      expect(normalizeKeys(["ctrl", "shift", "z"])).toEqual(["Ctrl", "Shift", "z"]);
    });

    test("should normalize window management shortcuts", () => {
      // Alt+Tab (window switching)
      expect(normalizeKeys(["alt", "tab"])).toEqual(["Alt", "Tab"]);

      // Win+D (show desktop)
      expect(normalizeKeys(["win", "d"])).toEqual(["Win", "d"]);

      // Alt+F4 (close window)
      expect(normalizeKeys(["alt", "f4"])).toEqual(["Alt", "F4"]);
    });

    test("should normalize text editing shortcuts", () => {
      // Shift+ArrowLeft (select text)
      expect(normalizeKeys(["shift", "arrowleft"])).toEqual(["Shift", "ArrowLeft"]);

      // Ctrl+A (select all)
      expect(normalizeKeys(["ctrl", "a"])).toEqual(["Ctrl", "a"]);

      // Ctrl+Home (go to beginning)
      expect(normalizeKeys(["ctrl", "home"])).toEqual(["Ctrl", "Home"]);
    });
  });
});

describe("GetSupportedKeyNames", () => {
  test("should return object with all categories", () => {
    const mappings = getSupportedKeyNames();

    expect(mappings).toHaveProperty("modifierKeys");
    expect(mappings).toHaveProperty("functionKeys");
    expect(mappings).toHaveProperty("arrowKeys");
    expect(mappings).toHaveProperty("fKeys");
    expect(mappings).toHaveProperty("specialChars");
  });

  test("should contain correct modifier key mappings", () => {
    const mappings = getSupportedKeyNames();

    expect(mappings.modifierKeys["ctrl"]).toBe("Ctrl");
    expect(mappings.modifierKeys["alt"]).toBe("Alt");
    expect(mappings.modifierKeys["shift"]).toBe("Shift");
  });

  test("should contain correct function key mappings", () => {
    const mappings = getSupportedKeyNames();

    expect(mappings.functionKeys["tab"]).toBe("Tab");
    expect(mappings.functionKeys["enter"]).toBe("Enter");
    expect(mappings.functionKeys["escape"]).toBe("Escape");
  });

  test("should contain correct arrow key mappings", () => {
    const mappings = getSupportedKeyNames();

    expect(mappings.arrowKeys["up"]).toBe("ArrowUp");
    expect(mappings.arrowKeys["down"]).toBe("ArrowDown");
    expect(mappings.arrowKeys["left"]).toBe("ArrowLeft");
    expect(mappings.arrowKeys["right"]).toBe("ArrowRight");
  });

  test("should contain correct F-key mappings", () => {
    const mappings = getSupportedKeyNames();

    expect(mappings.fKeys["f1"]).toBe("F1");
    expect(mappings.fKeys["f12"]).toBe("F12");
    expect(mappings.fKeys["f24"]).toBe("F24");
  });
});
