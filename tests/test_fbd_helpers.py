"""Tests for FBD-specific input helpers."""

import unittest

from helper_functions.fbd import (
    format_date,
    format_phone,
    normalize_registration,
    split_mobile_phone,
    split_month_year,
)


class FBDHelperTests(unittest.TestCase):
    """Verify values are normalized before reaching the FBD form."""

    def test_normalize_registration(self):
        """Registration separators are removed and letters are uppercased."""
        self.assertEqual(normalize_registration("12-d 12345"), "12D12345")

    def test_normalize_registration_rejects_blank_value(self):
        """A registration is required."""
        with self.assertRaisesRegex(ValueError, "vehicle registration"):
            normalize_registration("")

    def test_format_phone(self):
        """Irish local and international phone numbers are normalized."""
        self.assertEqual(format_phone("083-812 8391"), "0838128391")
        self.assertEqual(format_phone("+353 83 812 8391"), "0838128391")

    def test_format_phone_rejects_invalid_value(self):
        """Invalid Irish phone numbers fail before browser automation."""
        with self.assertRaisesRegex(ValueError, "Irish phone number"):
            format_phone("123")

    def test_split_mobile_phone(self):
        """FBD's prefix and remaining-digit fields are populated separately."""
        self.assertEqual(split_mobile_phone("083-812 8391"), ("083", "8128391"))

    def test_split_mobile_phone_rejects_landline(self):
        """The Irish-mobile path rejects unsupported prefixes."""
        with self.assertRaisesRegex(ValueError, "mobile prefix"):
            split_mobile_phone("01 234 5678")

    def test_format_date(self):
        """Configured dates are converted to FBD's display format."""
        self.assertEqual(format_date("11-01-1999"), "11/01/1999")

    def test_format_date_rejects_invalid_value(self):
        """Unsupported date formats are rejected."""
        with self.assertRaisesRegex(ValueError, "DD-MM-YYYY"):
            format_date("1999-01-11")

    def test_split_month_year(self):
        """Month/year controls receive FBD's visible option labels."""
        self.assertEqual(split_month_year("15-06-2023"), ("June", "2023"))


if __name__ == "__main__":
    unittest.main()
