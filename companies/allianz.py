"""Allianz Ireland car insurance automation."""

from playwright.async_api import Playwright, async_playwright

from data_maps.allianz import ALLIANZ_MAPPINGS
from helper_functions.allianz import accept_cookies

ALLIANZ_QUOTE_URL = "https://quote.allianz.ie/motorb2cui/"


async def open_quote_form(page):
    """Open Allianz Ireland and enter the car quote journey."""
    await page.goto(ALLIANZ_QUOTE_URL, wait_until="domcontentloaded")
    await accept_cookies(page)

    quote_link = page.get_by_role("link", name="Get car quote", exact=False).first
    await quote_link.wait_for(state="visible")
    await quote_link.click()
    await page.wait_for_load_state("domcontentloaded")


async def fill_vehicle_details(page, data):
    """Fill the Allianz vehicle section."""
    raise NotImplementedError("Allianz vehicle details are not implemented yet")


async def fill_personal_details(page, data):
    """Fill the Allianz personal-details section."""
    raise NotImplementedError("Allianz personal details are not implemented yet")


async def fill_driving_history(page, data):
    """Fill the Allianz driving-history section."""
    raise NotImplementedError("Allianz driving history is not implemented yet")


async def fill_cover_details(page, data):
    """Fill the Allianz cover section."""
    raise NotImplementedError("Allianz cover details are not implemented yet")


async def submit_quote(page):
    """Submit the Allianz quote form."""
    raise NotImplementedError("Allianz quote submission is not implemented yet")


async def extract_quote(page, data):
    """Extract and persist the Allianz quote result."""
    raise NotImplementedError("Allianz quote extraction is not implemented yet")


async def run(playwright: Playwright, data):
    """Run the Allianz quote journey."""
    browser = await playwright.chromium.launch(headless=False)

    try:
        page = await browser.new_page(locale="en-IE", timezone_id="Europe/Dublin")
        await open_quote_form(page)

        # Implement these sections in the order Allianz presents them.
        await fill_vehicle_details(page, data)
        await fill_personal_details(page, data)
        await fill_driving_history(page, data)
        await fill_cover_details(page, data)
        await submit_quote(page)
        await extract_quote(page, data)
    finally:
        await browser.close()


def supported_mappings():
    """Return the mapping keys currently defined for Allianz."""
    return tuple(ALLIANZ_MAPPINGS)


async def main(data):
    """Run Allianz as a standalone provider."""
    async with async_playwright() as playwright:
        await run(playwright, data)
