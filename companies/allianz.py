"""Allianz Ireland car insurance automation."""

import time

from playwright.async_api import Playwright, async_playwright

from data_maps.allianz import ALLIANZ_MAPPINGS
from helper_functions.allianz import (
    accept_cookies,
    format_date,
    format_mobile,
    gender_from_data,
)

ALLIANZ_QUOTE_URL = "https://quote.allianz.ie/motorb2cui/"


async def open_quote_form(page):
    """Open Allianz Ireland and enter the car quote journey."""
    await page.goto(ALLIANZ_QUOTE_URL, wait_until="domcontentloaded")
    await accept_cookies(page)

    first_name = page.locator("#firstName")
    try:
        await first_name.wait_for(state="visible", timeout=3_000)
    except Exception:
        quote_link = page.get_by_role("link", name="Get car quote", exact=False).first
        await quote_link.wait_for(state="visible")
        await quote_link.click()
        await page.wait_for_load_state("domcontentloaded")
        await first_name.wait_for(state="visible")


async def fill_vehicle_details(page, data):
    """Fill the Allianz vehicle section."""
    raise NotImplementedError("Allianz vehicle details are not implemented yet")


async def fill_personal_details(page, data):
    """Fill every field on Allianz's first, Your Details, page."""
    print("\n--- Filling Allianz Your Details page ---")

    required_fields = (
        "first_name",
        "last_name",
        "phone",
        "date_of_birth",
        "email",
        "occupation",
        "address",
        "policy_start_date",
    )
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        raise ValueError(f"Missing Allianz first-page data: {', '.join(missing)}")

    async def select_toggle(track_id, attribute, value):
        toggle = page.locator(
            f'nx-radio-toggle-button[trackid="{track_id}"]' f'[{attribute}="{value}"]'
        )
        await toggle.wait_for(state="visible")
        await toggle.locator("label").click()

    async def select_autocomplete(input_selector, query):
        search_input = page.locator(input_selector)
        await search_input.wait_for(state="visible")
        await search_input.fill(str(query))

        option = page.locator(
            "nx-autocomplete [role='option']:visible, "
            "nx-autocomplete nx-autocomplete-option:visible, "
            "[role='listbox'] [role='option']:visible"
        ).first
        await option.wait_for(state="visible", timeout=10_000)
        await option.click()

    await page.locator("#firstName").fill(data["first_name"])
    await page.locator("#surname").fill(data["last_name"])
    await page.locator("#mobileNumber").fill(format_mobile(data["phone"]))
    await page.locator("#dateOfBirth").fill(format_date(data["date_of_birth"]))
    await page.locator("#email").fill(data["email"])

    gender = gender_from_data(data)
    try:
        gender_label = ALLIANZ_MAPPINGS["gender"][gender]
    except KeyError as error:
        allowed = ", ".join(ALLIANZ_MAPPINGS["gender"])
        raise ValueError(
            f"Unsupported Allianz gender '{gender}'; use {allowed}"
        ) from error
    await select_toggle("Gender", "data-gender", gender_label)

    marketing = page.locator("#nx-checkbox-subMarketing")
    await marketing.set_checked(data.get("marketing_consent", False), force=True)

    employment_status = data.get("employment_status", "employed")
    try:
        employment_label = ALLIANZ_MAPPINGS["employment_status"][employment_status]
    except KeyError as error:
        allowed = ", ".join(ALLIANZ_MAPPINGS["employment_status"])
        raise ValueError(
            f"Unsupported Allianz employment status '{employment_status}'; use {allowed}"
        ) from error
    await select_toggle("employmentStatus", "data-shared-component", employment_label)

    occupation_input = page.locator("#occupationInput")
    if await occupation_input.count():
        await select_autocomplete("#occupationInput", data["occupation"])

    address = data["address"]
    address_query = address.get("postal_code") or ", ".join(
        part
        for part in (
            address.get("street"),
            address.get("city"),
            address.get("county"),
        )
        if part
    )
    if not address_query:
        raise ValueError("Allianz requires an Eircode or address search value")
    await select_autocomplete("#eirCode", address_query)
    await page.locator("#addressLine1").wait_for(state="visible")

    await select_toggle(
        "sameRiskAddress",
        "trackvalue",
        str(data.get("car_parked_at_home", True)).lower(),
    )
    await select_toggle(
        "isMultipolicy",
        "trackvalue",
        str(data.get("existing_allianz_policy", False)).lower(),
    )
    await page.locator('input[formcontrolname="coverDate"]').fill(
        format_date(data["policy_start_date"])
    )

    terms = page.locator("azire-terms-conditions input[type='checkbox']")
    await terms.set_checked(data.get("accept_terms", False), force=True)
    print("Completed Allianz Your Details fields")

    # sleep for 10 seconds
    time.sleep(6)


async def fill_driving_history(page, data):
    """Fill the Allianz driving-history section."""
    raise NotImplementedError("Allianz driving history is not implemented yet")


async def fill_cover_details(page, data):
    """Fill the Allianz cover section."""
    raise NotImplementedError("Allianz cover details are not implemented yet")


async def submit_quote(page):
    """Submit the first page and wait for Allianz's Car Details page."""
    button = page.locator("#clientDetailsSubmit")
    await button.wait_for(state="visible")
    await button.click()
    await button.wait_for(state="hidden", timeout=15_000)
    print("Proceeded to Allianz Car Details")


async def extract_quote(page, data):
    """Extract and persist the Allianz quote result."""
    raise NotImplementedError("Allianz quote extraction is not implemented yet")


async def run(playwright: Playwright, data):
    """Automate Allianz's first quote page."""
    browser = await playwright.chromium.launch(headless=False)

    try:
        page = await browser.new_page(locale="en-IE", timezone_id="Europe/Dublin")
        await open_quote_form(page)
        await fill_personal_details(page, data)
        await submit_quote(page)
    finally:
        await browser.close()


def supported_mappings():
    """Return the mapping keys currently defined for Allianz."""
    return tuple(ALLIANZ_MAPPINGS)


async def main(data):
    """Run Allianz as a standalone provider."""
    async with async_playwright() as playwright:
        await run(playwright, data)
