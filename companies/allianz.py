"""Allianz Ireland car insurance automation."""

import time

from playwright.async_api import Playwright, async_playwright

from data_maps.allianz import ALLIANZ_MAPPINGS
from helper_functions.allianz import (
    accept_cookies,
    business_mileage_value,
    format_date,
    format_mobile,
    format_registration,
    gender_from_data,
    mileage_option_matches,
    purchase_year,
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
    """Fill every field on Allianz's second, Car Details, page."""
    print("\n--- Filling Allianz Car Details page ---")

    required_fields = (
        "car_registration",
        "car_value",
        "car_purchase_date",
        "estimated_mileage",
    )
    missing = [field for field in required_fields if data.get(field) is None]
    if missing:
        raise ValueError(f"Missing Allianz car-page data: {', '.join(missing)}")

    async def select_toggle(track_id, value):
        toggle = page.locator(
            f'nx-radio-toggle-button[trackid="{track_id}"][trackvalue="{value}"]'
        )
        await toggle.wait_for(state="visible")
        await toggle.locator("label").click()

    registration = page.locator('input[formcontrolname="carRegistrationNumber"]')
    await registration.wait_for(state="visible")
    registration_value = format_registration(data["car_registration"])
    if not registration_value:
        raise ValueError("Allianz requires an alphanumeric car registration")
    await registration.fill(registration_value)
    registration_search = page.locator("azire-car-registration nx-page-search")
    await registration_search.get_by_role("button", name="Find", exact=True).click()
    await page.locator("azire-vrn-selected-car nx-message").wait_for(
        state="visible", timeout=15_000
    )

    await page.locator('input[formcontrolname="value"]').fill(str(data["car_value"]))
    await page.locator('input[formcontrolname="yearVehiclePurchased"]').fill(
        purchase_year(data["car_purchase_date"])
    )

    mileage_dropdown = page.locator(
        'azire-generic-dropdown[nameofcontrol="annualMileage"] nx-dropdown'
    )
    await mileage_dropdown.click()
    mileage_options = page.locator(
        "[role='listbox'] [role='option']:visible, nx-dropdown-item:visible"
    )
    await mileage_options.first.wait_for(state="visible")
    option_labels = await mileage_options.all_inner_texts()
    matching_index = next(
        (
            index
            for index, label in enumerate(option_labels)
            if mileage_option_matches(label, data["estimated_mileage"])
        ),
        None,
    )
    if matching_index is None:
        labels = ", ".join(label.strip() for label in option_labels)
        raise ValueError(
            f"No Allianz mileage option contains {data['estimated_mileage']}: {labels}"
        )
    await mileage_options.nth(matching_index).click()

    business_use = data.get("business_use", False)
    await select_toggle("businessUse", str(business_use).lower())
    if business_use:
        if data.get("business_mileage") is None:
            raise ValueError("Allianz requires 'business_mileage' for business use")
        await select_toggle(
            "businessMileage", business_mileage_value(data["business_mileage"])
        )
        await select_toggle(
            "solicitingOrders",
            str(data.get("soliciting_orders", False)).lower(),
        )
    else:
        await select_toggle(
            "commuting",
            str(data.get("commuting", False)).lower(),
        )

    other_vehicle_access = data.get("regular_use_other_vehicle", False)
    await select_toggle("accessToAnotherCar", str(other_vehicle_access).lower())
    if other_vehicle_access:
        vehicle_types = data.get("other_vehicle_types", [])
        if not vehicle_types:
            raise ValueError(
                "Allianz requires at least one 'other_vehicle_types' value when "
                "regular use of another vehicle is selected"
            )
        for vehicle_type in vehicle_types:
            try:
                form_value = ALLIANZ_MAPPINGS["other_vehicle_types"][vehicle_type]
            except KeyError as error:
                allowed = ", ".join(ALLIANZ_MAPPINGS["other_vehicle_types"])
                raise ValueError(
                    f"Unsupported other vehicle type '{vehicle_type}'; use {allowed}"
                ) from error
            checkbox = page.locator(
                'input[name="accessToAnotherCarValue"]' f'[value="{form_value}"]'
            )
            await checkbox.set_checked(True, force=True)

    print("Completed Allianz Car Details fields")


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


async def submit_vehicle_details(page):
    """Submit the second page and wait for Allianz's Driver Details page."""
    button = page.locator("#clientDetailsSubmit")
    await button.wait_for(state="visible")
    await button.click()
    await button.wait_for(state="hidden", timeout=15_000)
    print("Proceeded to Allianz Driver Details")


async def extract_quote(page, data):
    """Extract and persist the Allianz quote result."""
    raise NotImplementedError("Allianz quote extraction is not implemented yet")


async def run(playwright: Playwright, data):
    """Automate Allianz's first two quote pages."""
    browser = await playwright.chromium.launch(headless=False)

    try:
        page = await browser.new_page(locale="en-IE", timezone_id="Europe/Dublin")
        await open_quote_form(page)
        await fill_personal_details(page, data)
        await submit_quote(page)
        await fill_vehicle_details(page, data)
        await submit_vehicle_details(page)
    finally:
        # sleep for 10 seconds
        time.sleep(10)
        await browser.close()


def supported_mappings():
    """Return the mapping keys currently defined for Allianz."""
    return tuple(ALLIANZ_MAPPINGS)


async def main(data):
    """Run Allianz as a standalone provider."""
    async with async_playwright() as playwright:
        await run(playwright, data)
