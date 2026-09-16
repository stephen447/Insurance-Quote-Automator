"""Helpers specific to the Allianz Ireland quote journey."""


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
