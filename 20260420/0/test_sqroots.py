import unittest
from prog import sqroots

class TestFunc(unittest.TestCase):
    def test_value1(self):
        """1 2 1"""
        self.assertEqual(sqroots("1 2 1"), str(-1.0))

    def test_value2(self):
        """1 2 3"""
        self.assertEqual(sqroots("1 2 3"), "")

    def test_value3(self):
        """1 2 0"""
        self.assertEqual(sqroots("1 2 0"), str(-0.0) + " " + str(-2.0))

    def test_zerodiv(self):
        """Zero division test."""
        with self.assertRaises(ZeroDivisionError):
            sqroots("0 1 2")

    def test_wrong_str(self):
        """wrong str -> int"""
        with self.assertRaises(ValueError):
            sqroots("as  asa s")
