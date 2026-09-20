"""Helpers specific to the Allianz Ireland quote journey."""

from helper_functions.general import format_phone


async def accept_cookies(page):
    """Accept the Allianz cookie banner when it is displayed."""
    selectors = (
        "#onetrust-accept-btn-handler",
        'button:has-text("Accept All")',
        'button:has-text("Accept all")',
        'button:has-text("Accept")',
    )

    for selector in selectors:
        try:
            await page.locator(selector).first.click(timeout=2_000)
            return True
        except Exception:
            continue

    return False


def format_date(date_string):
    """Convert the project's DD-MM-YYYY dates to DD/MM/YYYY."""
    return date_string.replace("-", "/")


def format_mobile(phone_number):
    """Return a phone number in the compact format accepted by Allianz."""
    return format_phone(phone_number)


def gender_from_data(data):
    """Return Allianz's gender label, allowing legacy title-based profiles."""
    gender = data.get("gender")
    if gender:
        return gender.strip().lower()

    title = data.get("title", "").strip().lower()
    title_genders = {
        "mr": "male",
        "mrs": "female",
        "ms": "female",
        "miss": "female",
    }
    try:
        return title_genders[title]
    except KeyError as error:
        raise ValueError(
            "Allianz requires 'gender' when it cannot be inferred from 'title'"
        ) from error
