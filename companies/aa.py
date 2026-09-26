"""AA Ireland car insurance automation."""

import re
from datetime import datetime

from playwright.async_api import Playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from data_maps.aa import AA_MAPPINGS
from helper_functions.aa import (
    compact_price,
    format_local_phone,
    format_quote_options,
    normalize_name,
    normalize_registration,
    split_date,
)

AA_QUOTE_URL = "https://www.theaa.ie/v2/car-insurance/journey/my-info#name"


async def accept_cookies(page):
    """Accept AA's cookie banner when it is displayed."""
    cookie_buttons = (
        page.locator("#onetrust-accept-btn-handler"),
        page.get_by_role("button", name="Accept All Cookies", exact=True),
    )

    for button in cookie_buttons:
        try:
            await button.first.click(timeout=3_000)
            print("Accepted AA cookies")
            return
        except Exception:
            continue

    print("AA cookie banner was not displayed")


async def open_quote_form(page):
    """Open the AA quote journey at its first personal-information step."""
    await page.goto(AA_QUOTE_URL, wait_until="domcontentloaded")
    await accept_cookies(page)
    await page.locator("form#name").wait_for(state="visible")


def question(page, question_id):
    """Return a form or section belonging to one AA question."""
    return page.locator(
        f'form[id="{question_id}"], section[id="{question_id}"], '
        f'div[id="{question_id}"].car-details'
    )


async def wait_for_hash(page, route_hash, timeout=15_000):
    """Wait until the AA single-page journey reaches a hash route."""
    await page.wait_for_url(re.compile(rf"#{re.escape(route_hash)}$"), timeout=timeout)


async def submit_question(page, question_id, next_hash):
    """Submit one AA form question and wait for its next hash route."""
    form = question(page, question_id)
    await form.locator('button[type="submit"]').click()
    await wait_for_hash(page, next_hash)


async def select_toggle(page, question_id, label, next_hash):
    """Select a button-style answer and wait for the next question."""
    container = question(page, question_id)
    await container.get_by_role("button", name=str(label), exact=True).click()
    await wait_for_hash(page, next_hash)


async def select_toggle_to_any(page, question_id, label, next_hashes):
    """Select a button answer whose next question is conditionally chosen."""
    container = question(page, question_id)
    await container.get_by_role("button", name=str(label), exact=True).click()
    hashes = "|".join(re.escape(value) for value in next_hashes)
    await page.wait_for_url(re.compile(rf"#(?:{hashes})$"))


async def select_dropdown(page, question_id, label, next_hash):
    """Select an option from an AA React Aria dropdown."""
    container = question(page, question_id)
    trigger = container.locator('button[aria-haspopup="listbox"]')
    await trigger.click()
    option = page.get_by_role("option", name=str(label), exact=True)
    await option.wait_for(state="visible")
    await option.click()
    await submit_question(page, question_id, next_hash)


async def first_combobox_option(page, search):
    """Return the first option controlled by a specific Headless UI combobox."""
    search_element = await search.element_handle()
    await page.wait_for_function(
        """element => {
            const listboxId = element.getAttribute('aria-controls');
            return listboxId && document.getElementById(listboxId)
                ?.querySelector('[role="option"]');
        }""",
        arg=search_element,
        timeout=10_000,
    )
    listbox_id = await search.get_attribute("aria-controls")
    return page.locator(f'[id="{listbox_id}"]').get_by_role("option").first


async def select_autocomplete(page, question_id, query, next_hash):
    """Search an AA combobox and select its first returned option."""
    container = question(page, question_id)
    search = container.locator('[role="combobox"]')
    await search.fill(str(query))
    option = await first_combobox_option(page, search)
    await option.wait_for(state="visible", timeout=10_000)
    selected_label = " ".join((await option.inner_text()).split())
    await option.click()
    await submit_question(page, question_id, next_hash)
    print(f"Selected AA {question_id}: {selected_label}")


async def fill_date(page, question_id, date_string, next_hash):
    """Fill an AA segmented date field and submit it."""
    parts = split_date(date_string)
    container = question(page, question_id)

    for part in ("day", "month", "year"):
        segment = container.locator(f'[role="spinbutton"][data-type="{part}"]')
        if await segment.count():
            await segment.fill(parts[part])

    await submit_question(page, question_id, next_hash)


async def fill_name_details(page, data):
    """Fill the first and last name fields on AA's opening step."""
    missing = [field for field in ("first_name", "last_name") if not data.get(field)]
    if missing:
        raise ValueError(f"Missing AA name data: {', '.join(missing)}")

    first_name = normalize_name(data["first_name"])
    last_name = normalize_name(data["last_name"])
    name_form = question(page, "name")
    await name_form.locator("#firstName").fill(first_name)
    await name_form.locator("#lastName").fill(last_name)
    print(f"Filled AA name details for {first_name} {last_name}")


async def submit_name_details(page):
    """Submit AA's name step and wait for the title step."""
    await submit_question(page, "name", "title")
    print("Proceeded to AA title step")


async def fill_vehicle_registration(page, data):
    """Look up the insured vehicle and continue when AA finds it."""
    registration = normalize_registration(data["car_registration"])
    registration_form = question(page, "car-registration")
    await registration_form.locator("#registration").fill(registration)
    await registration_form.locator('button[type="submit"]').click()
    await page.wait_for_url(
        re.compile(r"#(?:car-details|car-not-found)$"), timeout=25_000
    )

    if page.url.endswith("#car-not-found"):
        raise ValueError(f"AA could not find vehicle registration '{registration}'")

    car_details = question(page, "car-details")
    await car_details.get_by_role("button", name="Continue", exact=True).click()
    await wait_for_hash(page, "address")
    print(f"AA found vehicle registration {registration}")


async def fill_address(page, data):
    """Search for and select the main driver's address."""
    address = data["address"]
    address_query = address.get("postal_code") or ", ".join(
        part
        for part in (address.get("street"), address.get("city"), address.get("county"))
        if part
    )
    if not address_query:
        raise ValueError("AA requires an Eircode or address search value")

    container = question(page, "address")
    search = container.locator('[role="combobox"]')
    await search.fill(address_query)
    option = await first_combobox_option(page, search)
    await option.wait_for(state="visible", timeout=10_000)
    await option.click()
    await container.locator('button[type="submit"]').click()
    await wait_for_hash(page, "employment-status", timeout=20_000)
    print("Selected AA address")


async def fill_email(page, email):
    """Fill AA's email step, including its conditional confirmation field."""
    email_form = question(page, "email")
    await email_form.locator('input[name="email"]').fill(email)
    await email_form.locator('button[type="submit"]').click()

    try:
        await wait_for_hash(page, "phone-number", timeout=10_000)
        return
    except PlaywrightTimeoutError:
        confirm_email = email_form.locator('input[name="confirmEmail"]')
        await confirm_email.wait_for(state="visible", timeout=5_000)
        await confirm_email.fill(email)
        await email_form.locator('button[type="submit"]').click()
        await wait_for_hash(page, "phone-number")


async def fill_personal_details(page, data):
    """Complete AA's My Info section for the main driver."""
    required = (
        "title",
        "first_name",
        "last_name",
        "date_of_birth",
        "email",
        "phone",
        "car_registration",
        "address",
        "employment_status",
        "occupation",
    )
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise ValueError(f"Missing AA personal data: {', '.join(missing)}")
    if data.get("add_additional_driver", False):
        raise NotImplementedError("AA additional-driver details are not implemented")

    await fill_name_details(page, data)
    await submit_name_details(page)

    try:
        title = AA_MAPPINGS["title"][data["title"].lower()]
    except KeyError as error:
        raise ValueError(f"Unsupported AA title '{data['title']}'") from error
    await select_toggle(page, "title", title, "dob")
    await fill_date(page, "dob", data["date_of_birth"], "email")

    await fill_email(page, data["email"])

    phone_form = question(page, "phone-number")
    await phone_form.locator("#phoneNumber").fill(format_local_phone(data["phone"]))
    await submit_question(page, "phone-number", "car-registration")
    await fill_vehicle_registration(page, data)
    await fill_address(page, data)

    employment_key = data["employment_status"].lower().replace(" ", "_")
    try:
        employment = AA_MAPPINGS["employment_status"][employment_key]
    except KeyError as error:
        raise ValueError(
            f"Unsupported AA employment status '{data['employment_status']}'"
        ) from error

    needs_job_details = employment in {"Employed", "Household Duties", "Self Employed"}
    employment_next = "industry" if needs_job_details else "additional-drivers"
    await select_dropdown(page, "employment-status", employment, employment_next)
    if needs_job_details:
        industry = data.get("industry", "Information Technology")
        await select_autocomplete(page, "industry", industry, "occupation")
        await select_autocomplete(
            page, "occupation", data["occupation"], "additional-drivers"
        )

    await select_toggle(page, "additional-drivers", "No", "registered-owner")
    print("Completed AA My Info section")


async def fill_vehicle_details(page, data):
    """Complete AA's My Car section for the supported owner path."""
    if data.get("registered_owner", "proposer") != "proposer":
        raise NotImplementedError("AA currently supports proposer-owned cars only")

    await select_toggle(page, "registered-owner", "Yes", "purchase-date")
    await fill_date(page, "purchase-date", data["car_purchase_date"], "seats")
    await select_dropdown(page, "seats", str(data.get("car_seats", 5)), "value")

    value_form = question(page, "value")
    await value_form.locator('input[name="value"]').fill(str(data["car_value"]))
    await submit_question(page, "value", "kilometers-per-year")

    mileage_form = question(page, "kilometers-per-year")
    await mileage_form.locator('input[name="kilometersPerYear"]').fill(
        str(data["estimated_mileage"])
    )
    await submit_question(page, "kilometers-per-year", "right-hand-drive")

    await select_toggle(
        page,
        "right-hand-drive",
        "Yes" if data.get("right_hand_drive", True) else "No",
        "imported",
    )
    await select_toggle(
        page,
        "imported",
        "Yes" if data.get("is_imported", False) else "No",
        "use-of-other-car",
    )
    await select_toggle(
        page,
        "use-of-other-car",
        "Yes" if data.get("regular_use_other_vehicle", False) else "No",
        "type",
    )
    print("Completed AA My Car section")


async def fill_licence_details(page, data):
    """Complete AA's My Licence section."""
    licence_key = data.get("licence_type", "full").lower()
    try:
        licence_type = AA_MAPPINGS["licence_type"][licence_key]
    except KeyError as error:
        raise ValueError(f"Unsupported AA licence type '{licence_key}'") from error

    if licence_type != "Full Irish":
        raise NotImplementedError("AA currently supports full Irish licences only")

    await select_toggle(page, "type", licence_type, "years")
    years_form = question(page, "years")
    await years_form.locator('input[name="years"]').fill(str(data["licence_duration"]))
    await submit_question(page, "years", "policy")
    print("Completed AA My Licence section")


async def fill_driving_history(page, data):
    """Complete AA's supported own-policy, no-claims history path."""
    if data.get("driving_experience", "myself") != "myself":
        raise NotImplementedError("AA currently supports own-policy experience only")
    if data.get("has_claims", False):
        raise NotImplementedError("AA claim details are not implemented")

    await select_toggle(page, "policy", "Yes", "policy-start-date")
    await fill_date(page, "policy-start-date", data["policy_start_date"], "ncb-years")

    ncd_years = min(int(data.get("no_claims_discount", 0)), 9)
    ncd_label = "9+" if ncd_years == 9 else str(ncd_years)
    await select_dropdown(page, "ncb-years", ncd_label, "ncb-origin")

    ncd_ireland = data.get("country_of_most_recent_ncd", "ireland").lower()
    if ncd_ireland != "ireland":
        raise NotImplementedError("AA currently supports Irish no-claims bonus only")
    await select_toggle(page, "ncb-origin", "Yes", "claims")
    await select_toggle_to_any(
        page,
        "claims",
        "No",
        ("payment-preference", "offers-and-discounts"),
    )
    print("Completed AA Driving History section")


async def fill_marketing_and_submit(page, data):
    """Complete AA's marketing questions and request the quote."""
    if page.url.endswith("#payment-preference"):
        payment_key = data.get("payment_type", "full")
        try:
            payment = AA_MAPPINGS["payment_type"][payment_key]
        except KeyError as error:
            raise ValueError(f"Unsupported AA payment type '{payment_key}'") from error
        await select_toggle_to_any(
            page,
            "payment-preference",
            payment,
            ("allow-phone-call", "offers-and-discounts"),
        )

    if page.url.endswith("#allow-phone-call"):
        await select_toggle(
            page,
            "allow-phone-call",
            "Yes" if data.get("phone_consent", False) else "No",
            "offers-and-discounts",
        )

    await select_toggle(
        page,
        "offers-and-discounts",
        "Yes" if data.get("marketing_consent", False) else "No",
        "terms-and-conditions",
    )
    if not data.get("accept_terms", False):
        raise ValueError("AA requires 'accept_terms' before requesting a quote")

    terms = question(page, "terms-and-conditions")
    await terms.get_by_role("button", name="Continue", exact=True).click()
    await page.wait_for_url(re.compile(r"/(?:quote|referral)(?:\?|$)"), timeout=45_000)
    print("Submitted AA quote request")


async def read_quote_cards(page):
    """Read every currently displayed AA quote card."""
    await page.evaluate("delete window.__aaQuoteCardState")
    await page.wait_for_function(
        """() => {
            const visible = element => element.offsetParent !== null;
            const loading = [...document.querySelectorAll(
                '.searching-better-price, .quote-card-skeleton'
            )].some(visible);
            const cards = [...document.querySelectorAll(
                '[data-testid="quote-card"]'
            )].filter(visible);
            const signature = cards.map(card => card.innerText).join('|');
            const now = Date.now();
            const previous = window.__aaQuoteCardState;

            if (loading || !previous || previous.signature !== signature) {
                window.__aaQuoteCardState = {signature, since: now};
                return false;
            }
            return cards.length > 0 && now - previous.since >= 2500;
        }""",
        timeout=60_000,
    )

    cards = page.locator('[data-testid="quote-card"]:visible')
    await cards.first.wait_for(state="visible", timeout=30_000)
    quotes = []
    for index in range(await cards.count()):
        card = cards.nth(index)
        cover_element = card.locator(".benefits-list-title").first
        if await cover_element.count():
            cover_labels = cover_element.locator(":scope > span")
            cover = " ".join((await cover_labels.first.inner_text()).split())
            membership = None
            if await cover_labels.count() > 1:
                membership = " ".join((await cover_labels.nth(1).inner_text()).split())
        else:
            cover = " ".join((await card.locator("header h3").inner_text()).split())
            membership = None

        recommended = await card.get_attribute("data-recommended") is not None
        if membership:
            variant = membership
        elif recommended:
            variant = "AA Membership recommendation"
        else:
            variant = "Standard cover"

        payments = {}
        for schedule in ("Annual", "Monthly"):
            tab = card.get_by_role("tab", name=schedule, exact=True)
            if await tab.is_disabled():
                payments[schedule] = {"available": False}
                continue

            await tab.click()
            await page.wait_for_function(
                "element => element.getAttribute('aria-selected') === 'true'",
                arg=await tab.element_handle(),
            )
            panel = card.locator('[role="tabpanel"]:visible').first
            await panel.wait_for(state="visible")

            plan_element = panel.locator(":scope > span").first
            plan = " ".join((await plan_element.inner_text()).split()).rstrip(":")
            price = compact_price(
                await panel.locator(":scope > .price-container").inner_text()
            )
            payment = {
                "available": True,
                "plan": plan,
                "price": price,
            }
            deposit = panel.locator(":scope > .deposit .price")
            if await deposit.count():
                payment["due_today"] = compact_price(await deposit.inner_text())
            payments[schedule] = payment

        quotes.append(
            {
                "cover": cover,
                "variant": variant,
                "payments": payments,
            }
        )
    return quotes


async def request_cover_level(page, cover_name):
    """Use AA's Tweak controls to request a quote for another cover level."""
    filters = page.locator(".tweak-cover-filters:visible").first
    if not await filters.count():
        await page.get_by_role("button", name="Tweak", exact=True).click()
        filters = page.locator(".tweak-cover-filters:visible").first
        await filters.wait_for(state="visible")

    cover_filter = filters.locator(".tweak-cover-filter").filter(has_text="Cover Level")
    await cover_filter.locator('button[aria-haspopup="listbox"]').click()
    option_pattern = re.compile(
        r"Third Party.*Fire.*Theft" if "Third Party" in cover_name else cover_name,
        re.IGNORECASE,
    )
    option = page.get_by_role("option", name=option_pattern).first
    try:
        await option.wait_for(state="visible", timeout=5_000)
    except PlaywrightTimeoutError:
        print(f"AA did not offer the '{cover_name}' cover-level option")
        return False
    await option.click()
    await filters.get_by_role("button", name="Update", exact=True).click()

    lower_cover = page.get_by_role(
        "button",
        name="Yes, Lower to Third Party Cover Only",
        exact=True,
    )
    try:
        await lower_cover.click(timeout=2_000)
    except PlaywrightTimeoutError:
        pass

    await page.wait_for_function(
        """target => [...document.querySelectorAll(
            '.benefits-list-title > span:first-child'
        )].some(element => element.textContent
            ?.toLowerCase().includes(target.toLowerCase()))""",
        arg="Third Party" if "Third Party" in cover_name else cover_name,
        timeout=45_000,
    )
    print(f"Requested AA cover level: {cover_name}")
    return True


async def extract_quote(page, data):
    """Append structured AA cover and payment prices to the report."""
    if "/referral" in page.url:
        raise RuntimeError("AA referred the quote instead of returning online prices")

    quotes = await read_quote_cards(page)
    covers = {quote["cover"].lower() for quote in quotes}
    if not any("third party" in cover for cover in covers):
        if await request_cover_level(page, "Third Party Fire & Theft"):
            third_party_quotes = [
                quote
                for quote in await read_quote_cards(page)
                if "third party" in quote["cover"].lower()
            ]
            quotes.extend(third_party_quotes)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("insurance_quotes.txt", "a", encoding="utf-8") as report:
        report.write("Company: AA Insurance\n")
        report.write(f"Quote Generated: {timestamp}\n")
        report.write(f"Vehicle: {data['car_registration']}\n")
        report.write(f"{'=' * 50}\n")
        report.write(format_quote_options(quotes))
        report.write("\n")
        report.write(f"{'=' * 50}\n\n")

    print("Saved AA quote options to insurance_quotes.txt")
    return quotes


async def run(playwright: Playwright, data):
    """Run the supported AA quote journey and record returned prices."""
    browser = await playwright.chromium.launch(headless=False)

    try:
        page = await browser.new_page(locale="en-IE", timezone_id="Europe/Dublin")
        await open_quote_form(page)
        await fill_personal_details(page, data)
        await fill_vehicle_details(page, data)
        await fill_licence_details(page, data)
        await fill_driving_history(page, data)
        await fill_marketing_and_submit(page, data)
        await extract_quote(page, data)
    finally:
        await browser.close()


def supported_mappings():
    """Return the mapping keys currently defined for AA."""
    return tuple(AA_MAPPINGS)


async def main(data):
    """Run AA as a standalone provider."""
    async with async_playwright() as playwright:
        await run(playwright, data)
