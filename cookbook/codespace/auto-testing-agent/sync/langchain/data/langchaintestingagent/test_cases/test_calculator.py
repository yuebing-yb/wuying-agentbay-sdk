import unittest
from calculator import Calculator, add, subtract, multiply, divide, is_even


class TestCalculatorClass(unittest.TestCase):
    """Test cases for the Calculator class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.calc = Calculator()

    def test_add_positive_numbers(self):
        """Test addition of positive numbers"""
        result = self.calc.add(3, 5)
        self.assertEqual(result, 8)

    def test_add_negative_numbers(self):
        """Test addition of negative numbers"""
        result = self.calc.add(-3, -5)
        self.assertEqual(result, -8)

    def test_add_mixed_numbers(self):
        """Test addition of positive and negative numbers"""
        result = self.calc.add(10, -3)
        self.assertEqual(result, 7)

    def test_add_floats(self):
        """Test addition of floating point numbers"""
        result = self.calc.add(3.5, 2.7)
        self.assertAlmostEqual(result, 6.2, places=1)

    def test_subtract_positive_numbers(self):
        """Test subtraction of positive numbers"""
        result = self.calc.subtract(10, 3)
        self.assertEqual(result, 7)

    def test_subtract_negative_numbers(self):
        """Test subtraction with negative numbers"""
        result = self.calc.subtract(-5, -3)
        self.assertEqual(result, -2)

    def test_subtract_mixed_numbers(self):
        """Test subtraction with mixed positive and negative numbers"""
        result = self.calc.subtract(5, -3)
        self.assertEqual(result, 8)

    def test_subtract_floats(self):
        """Test subtraction of floating point numbers"""
        result = self.calc.subtract(10.5, 3.2)
        self.assertAlmostEqual(result, 7.3, places=1)

    def test_multiply_positive_numbers(self):
        """Test multiplication of positive numbers"""
        result = self.calc.multiply(4, 6)
        self.assertEqual(result, 24)

    def test_multiply_negative_numbers(self):
        """Test multiplication with negative numbers"""
        result = self.calc.multiply(-4, -6)
        self.assertEqual(result, 24)

    def test_multiply_mixed_numbers(self):
        """Test multiplication with mixed positive and negative numbers"""
        result = self.calc.multiply(4, -6)
        self.assertEqual(result, -24)

    def test_multiply_by_zero(self):
        """Test multiplication by zero"""
        result = self.calc.multiply(5, 0)
        self.assertEqual(result, 0)

    def test_multiply_floats(self):
        """Test multiplication of floating point numbers"""
        result = self.calc.multiply(3.5, 2.0)
        self.assertEqual(result, 7.0)

    def test_divide_positive_numbers(self):
        """Test division of positive numbers"""
        result = self.calc.divide(15, 3)
        self.assertEqual(result, 5.0)

    def test_divide_negative_numbers(self):
        """Test division with negative numbers"""
        result = self.calc.divide(-15, -3)
        self.assertEqual(result, 5.0)

    def test_divide_mixed_numbers(self):
        """Test division with mixed positive and negative numbers"""
        result = self.calc.divide(15, -3)
        self.assertEqual(result, -5.0)

    def test_divide_floats(self):
        """Test division of floating point numbers"""
        result = self.calc.divide(7.5, 2.5)
        self.assertEqual(result, 3.0)

    def test_divide_by_zero_raises_value_error(self):
        """Test that division by zero raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.calc.divide(10, 0)
        self.assertEqual(str(context.exception), "Divisor cannot be zero")


class TestStandaloneFunctions(unittest.TestCase):
    """Test cases for standalone functions"""

    def test_add_function(self):
        """Test standalone add function"""
        result = add(3, 5)
        self.assertEqual(result, 8)

    def test_subtract_function(self):
        """Test standalone subtract function"""
        result = subtract(10, 3)
        self.assertEqual(result, 7)

    def test_multiply_function(self):
        """Test standalone multiply function"""
        result = multiply(4, 6)
        self.assertEqual(result, 24)

    def test_divide_function(self):
        """Test standalone divide function"""
        result = divide(15, 3)
        self.assertEqual(result, 5.0)

    def test_divide_function_by_zero_raises_zero_division_error(self):
        """Test that standalone divide function raises ZeroDivisionError"""
        with self.assertRaises(ZeroDivisionError) as context:
            divide(10, 0)
        self.assertEqual(str(context.exception), "Divisor cannot be zero")

    def test_is_even_with_even_number(self):
        """Test is_even function with even number"""
        result = is_even(4)
        self.assertTrue(result)

    def test_is_even_with_odd_number(self):
        """Test is_even function with odd number"""
        result = is_even(5)
        self.assertFalse(result)

    def test_is_even_with_negative_even_number(self):
        """Test is_even function with negative even number"""
        result = is_even(-4)
        self.assertTrue(result)

    def test_is_even_with_negative_odd_number(self):
        """Test is_even function with negative odd number"""
        result = is_even(-5)
        self.assertFalse(result)

    def test_is_even_with_zero(self):
        """Test is_even function with zero"""
        result = is_even(0)
        self.assertTrue(result)

    def test_is_even_with_non_integer_raises_type_error(self):
        """Test that is_even raises TypeError for non-integer input"""
        with self.assertRaises(TypeError) as context:
            is_even(3.5)
        self.assertEqual(str(context.exception), "Input must be an integer")
        
        with self.assertRaises(TypeError) as context:
            is_even("4")
        self.assertEqual(str(context.exception), "Input must be an integer")


if __name__ == '__main__':
    unittest.main()