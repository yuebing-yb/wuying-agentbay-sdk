"""
Unit tests for key name normalization functionality.
"""

import pytest

from agentbay._common.utils.key_normalizer import (
    _normalize_single_key,
    get_supported_key_names,
    normalize_keys,
)


class TestNormalizeSingleKey:
    """Test cases for _normalize_single_key function."""

    def test_lowercase_letters(self):
        """Test that lowercase letters remain lowercase."""
        assert _normalize_single_key("a") == "a"
        assert _normalize_single_key("z") == "z"
        assert _normalize_single_key("m") == "m"

    def test_uppercase_letters(self):
        """Test that uppercase letters are converted to lowercase."""
        assert _normalize_single_key("A") == "a"
        assert _normalize_single_key("Z") == "z"
        assert _normalize_single_key("M") == "m"

    def test_numbers(self):
        """Test that numbers remain unchanged."""
        assert _normalize_single_key("0") == "0"
        assert _normalize_single_key("5") == "5"
        assert _normalize_single_key("9") == "9"

    def test_modifier_keys_lowercase(self):
        """Test modifier keys in lowercase are converted to Title Case."""
        assert _normalize_single_key("ctrl") == "Ctrl"
        assert _normalize_single_key("alt") == "Alt"
        assert _normalize_single_key("shift") == "Shift"
        assert _normalize_single_key("win") == "Win"
        assert _normalize_single_key("meta") == "Meta"

    def test_modifier_keys_uppercase(self):
        """Test modifier keys in uppercase are converted to Title Case."""
        assert _normalize_single_key("CTRL") == "Ctrl"
        assert _normalize_single_key("ALT") == "Alt"
        assert _normalize_single_key("SHIFT") == "Shift"
        assert _normalize_single_key("WIN") == "Win"
        assert _normalize_single_key("META") == "Meta"

    def test_modifier_keys_titlecase(self):
        """Test modifier keys in Title Case remain unchanged."""
        assert _normalize_single_key("Ctrl") == "Ctrl"
        assert _normalize_single_key("Alt") == "Alt"
        assert _normalize_single_key("Shift") == "Shift"
        assert _normalize_single_key("Win") == "Win"
        assert _normalize_single_key("Meta") == "Meta"

    def test_function_keys_lowercase(self):
        """Test function keys in lowercase are converted to Title Case."""
        assert _normalize_single_key("tab") == "Tab"
        assert _normalize_single_key("enter") == "Enter"
        assert _normalize_single_key("escape") == "Escape"
        assert _normalize_single_key("backspace") == "Backspace"
        assert _normalize_single_key("delete") == "Delete"

    def test_function_keys_uppercase(self):
        """Test function keys in uppercase are converted to Title Case."""
        assert _normalize_single_key("TAB") == "Tab"
        assert _normalize_single_key("ENTER") == "Enter"
        assert _normalize_single_key("ESCAPE") == "Escape"
        assert _normalize_single_key("BACKSPACE") == "Backspace"
        assert _normalize_single_key("DELETE") == "Delete"

    def test_function_keys_titlecase(self):
        """Test function keys in Title Case remain unchanged."""
        assert _normalize_single_key("Tab") == "Tab"
        assert _normalize_single_key("Enter") == "Enter"
        assert _normalize_single_key("Escape") == "Escape"
        assert _normalize_single_key("Backspace") == "Backspace"
        assert _normalize_single_key("Delete") == "Delete"

    def test_arrow_keys_lowercase(self):
        """Test arrow keys in lowercase are converted to proper format."""
        assert _normalize_single_key("arrowup") == "ArrowUp"
        assert _normalize_single_key("arrowdown") == "ArrowDown"
        assert _normalize_single_key("arrowleft") == "ArrowLeft"
        assert _normalize_single_key("arrowright") == "ArrowRight"
        assert _normalize_single_key("up") == "ArrowUp"
        assert _normalize_single_key("down") == "ArrowDown"
        assert _normalize_single_key("left") == "ArrowLeft"
        assert _normalize_single_key("right") == "ArrowRight"

    def test_arrow_keys_uppercase(self):
        """Test arrow keys in uppercase are converted to proper format."""
        assert _normalize_single_key("ARROWUP") == "ArrowUp"
        assert _normalize_single_key("ARROWDOWN") == "ArrowDown"
        assert _normalize_single_key("ARROWLEFT") == "ArrowLeft"
        assert _normalize_single_key("ARROWRIGHT") == "ArrowRight"
        assert _normalize_single_key("UP") == "ArrowUp"
        assert _normalize_single_key("DOWN") == "ArrowDown"

    def test_f_keys_lowercase(self):
        """Test F-keys in lowercase are converted to correct format."""
        assert _normalize_single_key("f1") == "F1"
        assert _normalize_single_key("f5") == "F5"
        assert _normalize_single_key("f12") == "F12"
        assert _normalize_single_key("f24") == "F24"

    def test_f_keys_uppercase(self):
        """Test F-keys in uppercase are converted to correct format."""
        assert _normalize_single_key("F1") == "F1"
        assert _normalize_single_key("F5") == "F5"
        assert _normalize_single_key("F12") == "F12"

    def test_key_aliases(self):
        """Test that key aliases are properly mapped."""
        assert _normalize_single_key("control") == "Ctrl"
        assert _normalize_single_key("windows") == "Win"
        assert _normalize_single_key("esc") == "Escape"
        assert _normalize_single_key("return") == "Enter"
        assert _normalize_single_key("del") == "Delete"
        assert _normalize_single_key("pgup") == "PageUp"
        assert _normalize_single_key("pgdn") == "PageDown"

    def test_empty_string(self):
        """Test that empty string is handled correctly."""
        assert _normalize_single_key("") == ""

    def test_unknown_keys(self):
        """Test that unknown keys are returned as-is."""
        # Already in good format
        assert _normalize_single_key("Custom") == "Custom"
        assert _normalize_single_key("SomeKey") == "SomeKey"


class TestNormalizeKeys:
    """Test cases for normalize_keys function."""

    def test_empty_list(self):
        """Test that empty list is handled correctly."""
        assert normalize_keys([]) == []

    def test_none_input(self):
        """Test that None input is handled correctly."""
        assert normalize_keys(None) == None

    def test_single_key(self):
        """Test normalization of a single key."""
        assert normalize_keys(["A"]) == ["a"]
        assert normalize_keys(["ctrl"]) == ["Ctrl"]

    def test_key_combination_lowercase(self):
        """Test normalization of key combinations in lowercase."""
        assert normalize_keys(["ctrl", "c"]) == ["Ctrl", "c"]
        assert normalize_keys(["alt", "tab"]) == ["Alt", "Tab"]
        assert normalize_keys(["ctrl", "shift", "z"]) == ["Ctrl", "Shift", "z"]

    def test_key_combination_uppercase(self):
        """Test normalization of key combinations in uppercase."""
        assert normalize_keys(["CTRL", "C"]) == ["Ctrl", "c"]
        assert normalize_keys(["ALT", "TAB"]) == ["Alt", "Tab"]
        assert normalize_keys(["WIN", "D"]) == ["Win", "d"]

    def test_key_combination_mixed_case(self):
        """Test normalization of key combinations in mixed case."""
        assert normalize_keys(["ctrl", "SHIFT", "Z"]) == ["Ctrl", "Shift", "z"]
        assert normalize_keys(["ALT", "tab"]) == ["Alt", "Tab"]
        assert normalize_keys(["Win", "e"]) == ["Win", "e"]

    def test_complex_combinations(self):
        """Test normalization of complex key combinations."""
        # Ctrl+Alt+Delete
        assert normalize_keys(["ctrl", "alt", "delete"]) == ["Ctrl", "Alt", "Delete"]

        # Ctrl+Shift+Esc
        assert normalize_keys(["CTRL", "SHIFT", "ESC"]) == ["Ctrl", "Shift", "Escape"]

        # Win+Ctrl+D
        assert normalize_keys(["win", "ctrl", "d"]) == ["Win", "Ctrl", "d"]

    def test_function_keys_in_combination(self):
        """Test function keys in combinations."""
        assert normalize_keys(["alt", "f4"]) == ["Alt", "F4"]
        assert normalize_keys(["ctrl", "f5"]) == ["Ctrl", "F5"]
        assert normalize_keys(["shift", "f12"]) == ["Shift", "F12"]

    def test_arrow_keys_in_combination(self):
        """Test arrow keys in combinations."""
        assert normalize_keys(["shift", "arrowup"]) == ["Shift", "ArrowUp"]
        assert normalize_keys(["ctrl", "arrowdown"]) == ["Ctrl", "ArrowDown"]
        assert normalize_keys(["alt", "left"]) == ["Alt", "ArrowLeft"]
        assert normalize_keys(["shift", "right"]) == ["Shift", "ArrowRight"]

    def test_preserves_numbers(self):
        """Test that number keys are preserved."""
        assert normalize_keys(["ctrl", "1"]) == ["Ctrl", "1"]
        assert normalize_keys(["alt", "5"]) == ["Alt", "5"]
        assert normalize_keys(["shift", "9"]) == ["Shift", "9"]

    def test_non_string_elements(self):
        """Test that non-string elements are preserved."""
        assert normalize_keys(["ctrl", None, "c"]) == ["Ctrl", None, "c"]
        assert normalize_keys([123, "alt"]) == [123, "Alt"]


class TestGetSupportedKeyNames:
    """Test cases for get_supported_key_names function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        result = get_supported_key_names()
        assert isinstance(result, dict)

    def test_contains_all_categories(self):
        """Test that all key categories are present."""
        result = get_supported_key_names()
        assert "modifier_keys" in result
        assert "function_keys" in result
        assert "arrow_keys" in result
        assert "f_keys" in result
        assert "special_chars" in result

    def test_modifier_keys_content(self):
        """Test modifier keys category content."""
        result = get_supported_key_names()
        modifier_keys = result["modifier_keys"]
        assert "ctrl" in modifier_keys
        assert modifier_keys["ctrl"] == "Ctrl"
        assert "alt" in modifier_keys
        assert modifier_keys["alt"] == "Alt"

    def test_function_keys_content(self):
        """Test function keys category content."""
        result = get_supported_key_names()
        function_keys = result["function_keys"]
        assert "tab" in function_keys
        assert function_keys["tab"] == "Tab"
        assert "enter" in function_keys
        assert function_keys["enter"] == "Enter"

    def test_arrow_keys_content(self):
        """Test arrow keys category content."""
        result = get_supported_key_names()
        arrow_keys = result["arrow_keys"]
        assert "arrowup" in arrow_keys
        assert arrow_keys["arrowup"] == "ArrowUp"
        assert "up" in arrow_keys
        assert arrow_keys["up"] == "ArrowUp"


class TestRealWorldUseCases:
    """Test real-world use cases for key normalization."""

    def test_common_shortcuts(self):
        """Test common keyboard shortcuts."""
        # Copy
        assert normalize_keys(["CTRL", "C"]) == ["Ctrl", "c"]

        # Paste
        assert normalize_keys(["ctrl", "v"]) == ["Ctrl", "v"]

        # Cut
        assert normalize_keys(["Ctrl", "X"]) == ["Ctrl", "x"]

        # Select All
        assert normalize_keys(["ctrl", "A"]) == ["Ctrl", "a"]

        # Undo
        assert normalize_keys(["ctrl", "z"]) == ["Ctrl", "z"]

        # Redo
        assert normalize_keys(["ctrl", "shift", "Z"]) == ["Ctrl", "Shift", "z"]

        # Save
        assert normalize_keys(["CTRL", "s"]) == ["Ctrl", "s"]

    def test_window_management(self):
        """Test window management shortcuts."""
        # Alt+Tab
        assert normalize_keys(["ALT", "TAB"]) == ["Alt", "Tab"]

        # Alt+F4
        assert normalize_keys(["alt", "f4"]) == ["Alt", "F4"]

        # Win+D (Show Desktop)
        assert normalize_keys(["WIN", "d"]) == ["Win", "d"]

        # Win+E (Explorer)
        assert normalize_keys(["win", "E"]) == ["Win", "e"]

        # Win+L (Lock)
        assert normalize_keys(["Windows", "l"]) == ["Win", "l"]

    def test_text_editing(self):
        """Test text editing shortcuts."""
        # Ctrl+Home
        assert normalize_keys(["ctrl", "home"]) == ["Ctrl", "Home"]

        # Ctrl+End
        assert normalize_keys(["CTRL", "END"]) == ["Ctrl", "End"]

        # Shift+Arrow
        assert normalize_keys(["shift", "arrowleft"]) == ["Shift", "ArrowLeft"]

        # Ctrl+Backspace
        assert normalize_keys(["ctrl", "BACKSPACE"]) == ["Ctrl", "Backspace"]
