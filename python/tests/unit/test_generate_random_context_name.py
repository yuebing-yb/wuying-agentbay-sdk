import re
import unittest

from agentbay._sync.agentbay import _generate_random_context_name


class TestGenerateRandomContextName(unittest.TestCase):
    """Test the _generate_random_context_name private function"""

    def test_generate_with_timestamp_default(self):
        """Test generating context name with timestamp (default behavior)"""
        name = _generate_random_context_name()

        # Should have format: YYYYMMDDHHMMSS_<random>
        self.assertIsNotNone(name)
        self.assertIn("_", name)

        # Check timestamp part (14 digits) and random part
        parts = name.split("_")
        self.assertEqual(len(parts), 2)
        self.assertEqual(len(parts[0]), 14)  # Timestamp is 14 digits
        self.assertEqual(len(parts[1]), 8)   # Default random length is 8

        # Verify timestamp is all digits
        self.assertTrue(parts[0].isdigit())

        # Verify random part is alphanumeric
        self.assertTrue(parts[1].isalnum())

    def test_generate_without_timestamp(self):
        """Test generating context name without timestamp"""
        name = _generate_random_context_name(8, False)

        # Should only have random part, no underscore
        self.assertIsNotNone(name)
        self.assertNotIn("_", name)
        self.assertEqual(len(name), 8)
        self.assertTrue(name.isalnum())

    def test_generate_custom_length(self):
        """Test generating context name with custom length"""
        name = _generate_random_context_name(16, False)

        # Should have specified length
        self.assertEqual(len(name), 16)
        self.assertTrue(name.isalnum())

    def test_generate_with_timestamp_custom_length(self):
        """Test generating context name with timestamp and custom length"""
        name = _generate_random_context_name(12, True)

        parts = name.split("_")
        self.assertEqual(len(parts), 2)
        self.assertEqual(len(parts[0]), 14)  # Timestamp is always 14 digits
        self.assertEqual(len(parts[1]), 12)  # Custom random length

    def test_timestamp_format(self):
        """Test that timestamp follows YYYYMMDDHHMMSS format"""
        name = _generate_random_context_name()

        timestamp_part = name.split("_")[0]

        # Parse timestamp
        year = int(timestamp_part[0:4])
        month = int(timestamp_part[4:6])
        day = int(timestamp_part[6:8])
        hour = int(timestamp_part[8:10])
        minute = int(timestamp_part[10:12])
        second = int(timestamp_part[12:14])

        # Basic validation
        self.assertGreaterEqual(year, 2025)
        self.assertGreaterEqual(month, 1)
        self.assertLessEqual(month, 12)
        self.assertGreaterEqual(day, 1)
        self.assertLessEqual(day, 31)
        self.assertGreaterEqual(hour, 0)
        self.assertLessEqual(hour, 23)
        self.assertGreaterEqual(minute, 0)
        self.assertLessEqual(minute, 59)
        self.assertGreaterEqual(second, 0)
        self.assertLessEqual(second, 59)

    def test_uniqueness(self):
        """Test that generated names are unique"""
        names = set()
        for _ in range(100):
            name = _generate_random_context_name()
            names.add(name)

        # Should have generated 100 unique names
        # (very unlikely to have collisions with 8 character random strings)
        self.assertEqual(len(names), 100)

    def test_character_set(self):
        """Test that only alphanumeric characters are used"""
        for _ in range(10):
            name = _generate_random_context_name(100, False)
            # Should only contain a-zA-Z0-9
            self.assertIsNotNone(re.match(r'^[a-zA-Z0-9]+$', name))


if __name__ == "__main__":
    unittest.main()
