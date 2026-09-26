"""Helpers for the AA Ireland quote journey."""

from datetime import datetime


def normalize_name(value):
    """Trim a name and collapse repeated whitespace before form entry."""
    if not isinstance(value, str):
        raise ValueError("AA name values must be strings")

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError("AA name values cannot be empty")
    return normalized


def normalize_registration(value):
    """Return an uppercase alphanumeric Irish registration."""
    normalized = "".join(character for character in str(value) if character.isalnum())
    if not normalized:
        raise ValueError("AA requires a vehicle registration")
    return normalized.upper()


def format_local_phone(value):
    """Return the local part entered after AA's fixed +353 prefix."""
    digits = "".join(character for character in str(value) if character.isdigit())
    if digits.startswith("353"):
        digits = digits[3:]
    digits = digits.lstrip("0")
    if not 7 <= len(digits) <= 10:
        raise ValueError("AA requires a valid Irish phone number")
    return digits


def split_date(value):
    """Parse a DD-MM-YYYY date into AA's segmented date values."""
    try:
        parsed = datetime.strptime(value, "%d-%m-%Y")
    except (TypeError, ValueError) as error:
        raise ValueError("AA dates must use DD-MM-YYYY format") from error
    return {
        "day": f"{parsed.day:02d}",
        "month": f"{parsed.month:02d}",
        "year": str(parsed.year),
    }


def compact_price(value):
    """Join the separately styled parts of an AA price into one value."""
    return "".join(str(value).split())


def format_quote_options(quotes):
    """Format structured AA quote cards for the comparison report."""
    lines = []
    for index, quote in enumerate(quotes, start=1):
        variant = quote.get("variant")
        heading = f"Quote option {index}"
        if variant:
            heading += f" ({variant})"
        lines.append(f"{heading}:")
        cover = quote["cover"]
        for schedule, payment in quote["payments"].items():
            if not payment.get("available", True):
                lines.append(f"  {cover} ({schedule}): Not available")
                continue

            plan = payment.get("plan")
            description = f"{schedule}, {plan}" if plan else schedule
            lines.append(f"  {cover} ({description}): {payment['price']}")
            if payment.get("due_today"):
                lines.append(f"    Due today: {payment['due_today']}")
        lines.append("")
    return "\n".join(lines)
