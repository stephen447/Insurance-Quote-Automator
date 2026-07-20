# Install: pip install playwright-stealth && playwright install chromium
import asyncio
from playwright_stealth import Stealth
from playwright.async_api import async_playwright
import companies.axa as axa
from main import PERSONAL_INFO


async def main():
    async with Stealth().use_async(async_playwright()) as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.axa.ie/car-insurance/")

        await axa.accept_cookies(page)
        await axa.fill_vehicle_details(page, PERSONAL_INFO)
        # await axa.fill_personal_details(page, PERSONAL_INFO)
        # await axa.fill_driving_history(page, PERSONAL_INFO)
        # await axa.fill_claims_history(page, PERSONAL_INFO)
        # await axa.fill_discounts(page, PERSONAL_INFO)
        # await axa.fill_cover_details(page, PERSONAL_INFO)

        await page.wait_for_timeout(10_000)
        await browser.close()

asyncio.run(main())
