"""Unit tests for Allianz data formatting helpers."""

import unittest

from helper_functions.allianz import (
    business_mileage_value,
    format_date,
    format_mobile,
    format_registration,
    gender_from_data,
    mileage_option_matches,
    purchase_year,
)


class AllianzHelperTests(unittest.TestCase):
    """Verify values are normalized before reaching the Allianz form."""

    def test_format_date(self):
        """Test Date format."""
        self.assertEqual(format_date("11-01-1999"), "11/01/1999")

    def test_format_mobile(self):
        """Test mobile format"""
        self.assertEqual(format_mobile("083-812 8391"), "0838128391")

    def test_format_registration_removes_special_characters(self):
        """Test Allianz receives only uppercase alphanumeric characters."""
        self.assertEqual(format_registration("12-D 12345"), "12D12345")

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

    def test_purchase_year(self):
        """Test extracting the vehicle purchase year."""
        self.assertEqual(purchase_year("15-06-2023"), "2023")

    def test_purchase_year_rejects_incomplete_date(self):
        """Test invalid vehicle purchase dates are rejected."""
        with self.assertRaisesRegex(ValueError, "DD-MM-YYYY"):
            purchase_year("June 2023")

    def test_mileage_matches_bounded_range(self):
        """Test matching an annual mileage against a bounded option."""
        self.assertTrue(mileage_option_matches("7,501 - 10,000 KM", 10_000))
        self.assertFalse(mileage_option_matches("5,001 - 7,500 KM", 10_000))

    def test_mileage_matches_open_ended_ranges(self):
        """Test matching mileage against upper and lower open ranges."""
        self.assertTrue(mileage_option_matches("Up to 5,000 KM", 4_000))
        self.assertTrue(mileage_option_matches("More than 50,000 KM", 60_000))

    def test_business_mileage_mapping(self):
        """Test Allianz's three business-mileage bands."""
        self.assertEqual(business_mileage_value(2_000), "M01")
        self.assertEqual(business_mileage_value(7_500), "M02")
        self.assertEqual(business_mileage_value(12_000), "M03")


if __name__ == "__main__":
    unittest.main()
