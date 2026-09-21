"""Helpers specific to the Allianz Ireland quote journey."""

import re

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


def format_registration(registration):
    """Remove unsupported characters from an Allianz registration number."""
    return re.sub(r"[^A-Za-z0-9]", "", str(registration)).upper()


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


def purchase_year(date_string):
    """Extract a four-digit purchase year from DD-MM-YYYY or DD/MM/YYYY."""
    year = re.split(r"[-/]", str(date_string))[-1]
    if not re.fullmatch(r"\d{4}", year):
        raise ValueError("Car purchase date must use DD-MM-YYYY or DD/MM/YYYY")
    return year


def mileage_option_matches(label, annual_mileage):
    """Return whether a rendered Allianz range contains the annual mileage."""
    normalized = " ".join(label.lower().split())
    values = [int(value.replace(",", "")) for value in re.findall(r"\d[\d,]*", label)]
    mileage = int(annual_mileage)

    if len(values) >= 2:
        return values[0] <= mileage <= values[1]
    if len(values) == 1:
        if any(word in normalized for word in ("more", "over", "above", "+")):
            return mileage > values[0]
        if any(
            phrase in normalized
            for phrase in ("up to", "less", "under", "below", "or less")
        ):
            return mileage <= values[0]
    return False


def business_mileage_value(annual_business_mileage):
    """Map numeric business mileage to Allianz's stable toggle value."""
    mileage = int(annual_business_mileage)
    if mileage < 0:
        raise ValueError("Business mileage cannot be negative")
    if mileage <= 2_000:
        return "M01"
    if mileage <= 10_000:
        return "M02"
    return "M03"
