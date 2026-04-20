import unittest
from prog import func

class TestFunc(unittest.TestCase):
    def test_value(self):
        """Normal value tests."""
        self.assertEqual(func(1, 2), 1 + 1 / 2)
        self.assertEqual(func(2, 3), 2 + 1 / 3)

    def test_zerodiv(self):
        """Zero division test."""
        with self.assertRaises(ZeroDivisionError):
            func(1, 0)
