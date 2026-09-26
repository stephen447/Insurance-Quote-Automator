"""Tests for AA-specific helper functions."""

import unittest

from helper_functions.aa import (
    compact_price,
    format_local_phone,
    format_quote_options,
    normalize_name,
    normalize_registration,
    split_date,
)


class AAHelperTests(unittest.TestCase):
    """Verify values are normalized before reaching the AA form."""

    def test_normalize_name_trims_and_collapses_whitespace(self):
        """Names are stripped and repeated whitespace is collapsed."""
        self.assertEqual(normalize_name("  Mary   Jane  "), "Mary Jane")

    def test_normalize_name_rejects_invalid_values(self):
        """Blank and non-string values are rejected."""
        for value in ("", "   ", None, 123):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_name(value)

    def test_normalize_registration(self):
        """Registration separators are removed and letters are uppercased."""
        self.assertEqual(normalize_registration("12-d 12345"), "12D12345")

    def test_format_local_phone(self):
        """AA receives only the local digits after its fixed +353 prefix."""
        self.assertEqual(format_local_phone("083-812 8391"), "838128391")
        self.assertEqual(format_local_phone("+353 83 812 8391"), "838128391")

    def test_split_date(self):
        """DD-MM-YYYY dates are split for segmented AA date fields."""
        self.assertEqual(
            split_date("11-01-1999"),
            {"day": "11", "month": "01", "year": "1999"},
        )

    def test_split_date_rejects_invalid_format(self):
        """Other date formats are rejected before browser automation."""
        with self.assertRaisesRegex(ValueError, "DD-MM-YYYY"):
            split_date("1999-01-11")

    def test_compact_price(self):
        """Separately styled currency parts become one report value."""
        self.assertEqual(compact_price("€\n613\n.53"), "€613.53")

    def test_format_quote_options_omits_card_content(self):
        """The report includes prices, not benefits or action labels."""
        quotes = [
            {
                "cover": "Fully Comprehensive",
                "variant": "Standard cover",
                "payments": {
                    "Annual": {
                        "available": True,
                        "plan": "1 full payment",
                        "price": "€613.53",
                    },
                    "Monthly": {
                        "available": True,
                        "plan": "11 monthly payments",
                        "price": "€56.00",
                        "due_today": "€57.53",
                    },
                },
            }
        ]

        formatted = format_quote_options(quotes)

        self.assertEqual(
            formatted,
            "Quote option 1 (Standard cover):\n"
            "  Fully Comprehensive (Annual, 1 full payment): €613.53\n"
            "  Fully Comprehensive (Monthly, 11 monthly payments): €56.00\n"
            "    Due today: €57.53\n",
        )
        self.assertNotIn("Continue", formatted)
        self.assertNotIn("Price breakdown", formatted)

    def test_format_quote_options_distinguishes_membership_card(self):
        """AA's adjacent membership recommendation remains identifiable."""
        quotes = [
            {
                "cover": "Fully Comprehensive",
                "variant": "Standard cover",
                "payments": {"Annual": {"plan": "1 full payment", "price": "€613.53"}},
            },
            {
                "cover": "Fully Comprehensive",
                "variant": "AA Membership benefits",
                "payments": {"Annual": {"plan": "1 full payment", "price": "€649.53"}},
            },
        ]

        formatted = format_quote_options(quotes)

        self.assertIn("Quote option 1 (Standard cover):", formatted)
        self.assertIn("Quote option 2 (AA Membership benefits):", formatted)
        self.assertIn("€613.53", formatted)
        self.assertIn("€649.53", formatted)


if __name__ == "__main__":
    unittest.main()
