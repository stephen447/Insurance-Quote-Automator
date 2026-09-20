"""Helpers shared by multiple insurance providers."""


def capitalize_first_letter(string):
    """Capitalize the first character of a string."""
    return string.capitalize()


def format_phone(phone):
    """Remove spaces and hyphens from a phone number."""
    return phone.replace(" ", "").replace("-", "")
