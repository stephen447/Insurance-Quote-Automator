"""Unit tests for Allianz data formatting helpers."""

import unittest

from helper_functions.allianz import format_date, format_mobile, gender_from_data


class AllianzHelperTests(unittest.TestCase):
    """Verify values are normalized before reaching the Allianz form."""

    def test_format_date(self):
        """Test Date format."""
        self.assertEqual(format_date("11-01-1999"), "11/01/1999")

    def test_format_mobile(self):
        """Test mobile format"""
        self.assertEqual(format_mobile("083-812 8391"), "0838128391")

    def test_explicit_gender_is_normalized(self):
        """Test gender format"""
        self.assertEqual(gender_from_data({"gender": " Male "}), "male")

    def test_gender_can_be_inferred_from_legacy_title(self):
        """Test geneder being inferred from title"""
        self.assertEqual(gender_from_data({"title": "Mrs"}), "female")

    def test_unknown_title_requires_gender(self):
        """Test unknown gender"""
        with self.assertRaisesRegex(ValueError, "requires 'gender'"):
            gender_from_data({"title": "Mx"})


if __name__ == "__main__":
    unittest.main()
