"""Input helpers for the FBD Ireland quote journey."""

from datetime import datetime


def normalize_registration(value):
    """Return an uppercase alphanumeric Irish vehicle registration."""
    normalized = "".join(character for character in str(value) if character.isalnum())
    if not normalized:
        raise ValueError("FBD requires a vehicle registration")
    return normalized.upper()


def format_phone(value):
    """Return an Irish phone number as digits with its leading zero."""
    digits = "".join(character for character in str(value) if character.isdigit())
    if digits.startswith("353"):
        digits = f"0{digits[3:]}"
    if not 9 <= len(digits) <= 10 or not digits.startswith("0"):
        raise ValueError("FBD requires a valid Irish phone number")
    return digits


def split_mobile_phone(value):
    """Split an Irish mobile number into FBD's prefix and local fields."""
    digits = format_phone(value)
    prefix = digits[:3]
    if prefix not in {"083", "085", "086", "087", "089"}:
        raise ValueError("FBD requires a supported Irish mobile prefix")
    return prefix, digits[3:]


def format_date(value):
    """Validate DD-MM-YYYY input and return DD/MM/YYYY for form entry."""
    try:
        parsed = datetime.strptime(value, "%d-%m-%Y")
    except (TypeError, ValueError) as error:
        raise ValueError("FBD dates must use DD-MM-YYYY format") from error
    return parsed.strftime("%d/%m/%Y")


def split_month_year(value):
    """Return the full month name and year from a DD-MM-YYYY date."""
    try:
        parsed = datetime.strptime(value, "%d-%m-%Y")
    except (TypeError, ValueError) as error:
        raise ValueError("FBD dates must use DD-MM-YYYY format") from error
    return parsed.strftime("%B"), str(parsed.year)
