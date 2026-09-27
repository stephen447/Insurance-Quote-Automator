"""FBD Ireland car-insurance automation boilerplate."""

import re

from playwright.async_api import Playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from data_maps.fbd import FBD_MAPPINGS
from helper_functions.fbd import (
    format_date,
    normalize_registration,
    split_mobile_phone,
    split_month_year,
)

FBD_QUOTE_URL = "https://www.fbd.ie/car-quote/your-details;step=1"


async def accept_cookies(page):
    """Accept FBD's cookie prompt when one is displayed."""
    # FBD has used both a OneTrust id and an accessible button across deployments.
    buttons = (
        page.locator("#onetrust-accept-btn-handler"),
        page.get_by_role(
            "button",
            name=re.compile(r"accept(?: all)?(?: cookies)?", re.IGNORECASE),
        ),
    )
    for button in buttons:
        try:
            # A short timeout keeps an absent cookie banner from slowing every run.
            await button.first.click(timeout=3_000)
            print("Accepted FBD cookies")
            return
        except PlaywrightTimeoutError:
            # Try the alternative selector before treating the banner as absent.
            continue


async def open_quote_form(page):
    """Open the first step of FBD's car-insurance quote journey."""
    await page.goto(
        FBD_QUOTE_URL,
        wait_until="domcontentloaded",
        timeout=45_000,
    )
    await accept_cookies(page)
    # The quote component appearing is a stronger readiness signal than page load.
    await page.locator("fbd-quote-input").wait_for(state="visible", timeout=30_000)

    # Returning visitors may no longer see the quotation-terms interstitial.
    agreement = page.get_by_role("button", name="I agree", exact=True)
    try:
        await agreement.click(timeout=3_000)
        print("Accepted FBD's quotation terms")
    except PlaywrightTimeoutError:
        # No action is needed when the terms were accepted in an earlier session.
        pass

    # Fail early if FBD redirects to maintenance, an error page, or another journey.
    if "/car-quote/your-details" not in page.url:
        raise RuntimeError(f"FBD did not open the expected quote journey: {page.url}")
    print(f"Opened FBD quote journey: {page.url}")
    return page.url


def form_group(page, key):
    """Locate an FBD form group by its stable test hook or element id."""
    # Prefer application-owned test hooks, with ids retained for older components.
    return page.locator(f'[data-test="{key}"], [data-hook="{key}"], #{key}').first


async def open_accordion(page, panel_id):
    """Open the next FBD section after its preceding form becomes valid."""
    header = page.locator(f'[role="button"][aria-controls="{panel_id}"]')
    await header.wait_for(state="visible")
    if await header.get_attribute("aria-expanded") == "true":
        return
    # FBD keeps later accordions disabled until Angular validates the prior one.
    await page.wait_for_function(
        "element => element.getAttribute('aria-disabled') !== 'true'",
        arg=await header.element_handle(),
        timeout=20_000,
    )
    await header.click()
    await page.locator(f"#{panel_id}").wait_for(state="visible")


async def fill_text(page, key, value):
    """Fill a visible text-like control and blur it for Angular validation."""
    group = form_group(page, key)
    await group.wait_for(state="visible")
    control = group.locator("input:not([type=radio]):not([type=checkbox])").first
    await control.fill(str(value))
    # Blurring is required for several FBD controls to run their validators.
    await control.press("Tab")


async def select_radio(page, key, label):
    """Select an FBD radio option using its accessible label suffix."""
    group = form_group(page, key)
    await group.wait_for(state="visible")
    # Playwright serializes this pattern as /.../; escape slashes in labels too.
    escaped_label = re.escape(str(label)).replace("/", r"\/")
    option = group.get_by_role(
        "radio",
        name=re.compile(rf"(?:^|,\s*){escaped_label}$", re.IGNORECASE),
    ).first
    await option.wait_for(state="attached")
    # Some radios exist before FBD enables them, so attachment alone is insufficient.
    await page.wait_for_function(
        """element => !element.disabled
            && element.getAttribute('aria-disabled') !== 'true'""",
        arg=await option.element_handle(),
        timeout=15_000,
    )
    await option.click(force=True)


async def select_boolean(page, key, value):
    """Select Yes or No within one FBD button group."""
    submitted_value = "true" if value else "false"
    hidden_input = form_group(page, key).locator(
        f'input[type="radio"][value="{submitted_value}"]'
    )
    # The input itself is hidden; the surrounding ARIA label is the click target.
    option = hidden_input.locator("xpath=ancestor::label[@role='radio']")
    await option.wait_for(state="visible")
    await option.click()
    # Confirm the custom label registered the click rather than trusting click success.
    await page.wait_for_function(
        "element => element.getAttribute('aria-checked') === 'true'",
        arg=await option.element_handle(),
        timeout=5_000,
    )


async def select_title(page, title_key):
    """Select FBD's hidden title radio by its verified submitted value."""
    # FBD submits numeric codes (for example, "04" for Mr), not visible labels.
    try:
        title_value = FBD_MAPPINGS["title"][title_key]
    except KeyError as error:
        raise ValueError(f"Unsupported FBD title '{title_key}'") from error

    title_input = form_group(page, "title-buttons").locator(
        f'input[type="radio"][value="{title_value}"]'
    )
    title_option = title_input.locator("xpath=ancestor::label[@role='radio']")
    await title_option.click()
    # The ARIA state is updated only after Angular accepts the title value.
    await page.wait_for_function(
        "element => element.getAttribute('aria-checked') === 'true'",
        arg=await title_option.element_handle(),
        timeout=5_000,
    )


async def select_dropdown(page, key, label):
    """Select an option from an FBD responsive dropdown."""
    group = form_group(page, key)
    await group.wait_for(state="visible")
    await select_responsive_dropdown(group, label)


async def select_responsive_dropdown(container, label):
    """Select through the native control that drives FBD's responsive UI."""
    # FBD renders a hidden native select and a custom desktop dropdown together.
    # Forcing the native control still emits the input/change events Angular needs.
    native = container.locator("select").first
    await native.wait_for(state="attached")
    await native.select_option(label=str(label), force=True)
    # Read the selected option back to catch stale or mismatched site labels quickly.
    selected_label = await native.locator("option:checked").inner_text()
    if selected_label.strip().lower() != str(label).strip().lower():
        raise RuntimeError(f"FBD did not select dropdown option '{label}'")


async def select_autocomplete(page, key, value, exact=True):
    """Fill one FBD typeahead and choose a returned visible option."""
    group = form_group(page, key)
    await group.wait_for(state="visible")
    control = group.locator('input[placeholder*="type or select"]').first
    await control.fill(str(value))
    # Occupations require an exact match; insurer names can use a partial match.
    if exact:
        option = group.locator('[role="option"]:visible').filter(
            has_text=re.compile(rf"^{re.escape(str(value))}$", re.IGNORECASE)
        )
    else:
        option = group.locator('[role="option"]:visible').filter(
            has_text=re.compile(re.escape(str(value)), re.IGNORECASE)
        )
    # Results are populated asynchronously after the user-facing input changes.
    await option.first.wait_for(state="visible")
    await option.first.click()


async def select_month_year(page, key, value):
    """Populate one of FBD's paired month/year dropdown controls."""
    month, year = split_month_year(value)
    group = form_group(page, key)
    await group.wait_for(state="visible")
    dropdowns = group.locator("fbd-dropdown")
    # These controls are ordered month first and year second in the component DOM.
    await select_responsive_dropdown(dropdowns.nth(0), month)
    await select_responsive_dropdown(dropdowns.nth(1), year)


async def select_year_count(page, key, years):
    """Choose an FBD duration option such as '4 Years' or '5+ Years'."""
    group = form_group(page, key)
    await group.wait_for(state="visible")
    option = group.get_by_role(
        "radio",
        # The form varies between "5+ Years" and "5 Years or more" wording.
        name=re.compile(
            rf"(?:^|,\s*)(?:{int(years)}(?:\+)?\s+Years?"
            rf"(?:\s+or\s+more)?|{int(years)}\s+or\s+more\s+Years?)$",
            re.IGNORECASE,
        ),
    ).first
    # Duration choices can be present but temporarily disabled during panel updates.
    await option.wait_for(state="attached", timeout=15_000)
    await option.click(force=True)


async def fill_address(page, data):
    """Search for and select the configured Irish home address."""
    group = form_group(page, "address")
    # An Eircode gives FBD's address service the least ambiguous search value.
    search_value = data["address"].get("postal_code") or data["address"]["street"]
    await group.locator("#addressInput").fill(search_value)
    await group.get_by_role("button", name="Search", exact=True).click()
    # Selecting a suggestion supplies FBD's internal address identifier as well as text.
    suggestion = group.locator('[role="option"]:visible').first
    try:
        await suggestion.click(timeout=10_000)
    except PlaywrightTimeoutError as error:
        # Only convert a genuine validation failure into a provider-specific error.
        if "form-group--invalid" in (await group.get_attribute("class") or ""):
            message = "FBD did not return a selectable home address"
            raise RuntimeError(message) from error


async def fill_about_you(page, data):
    """Complete FBD's About You accordion for the main policyholder."""
    # Complete fields in display order so Angular reveals dependent questions.
    # Dates are converted from the repository's DD-MM-YYYY format to FBD's slashes.
    await fill_text(page, "policy-start-date", format_date(data["policy_start_date"]))
    await select_title(page, data["title"])
    await fill_text(page, "firstName", data["first_name"])
    await fill_text(page, "lastName", data["last_name"])
    await fill_text(page, "dateOfBirth", format_date(data["date_of_birth"]))
    await fill_address(page, data)
    await select_boolean(page, "parkOvernight", data.get("car_parked_at_home", True))

    employment = FBD_MAPPINGS["employment_status"][data["employment_status"]]
    await select_dropdown(page, "employmentStatus", employment)
    # Occupation questions are only relevant for working policyholders.
    if data["employment_status"] in {"employed", "self_employed"}:
        occupation = FBD_MAPPINGS["occupation"].get(
            data["occupation"].lower(), data["occupation"]
        )
        # Fall back to the configured label when no provider-specific alias is needed.
        await select_autocomplete(page, "occupation", occupation)
        has_part_time = data.get("has_part_time_occupation", False)
        part_time_group = form_group(page, "employedPartTime")
        # FBD only inserts this follow-up for occupation combinations that need it.
        try:
            await part_time_group.wait_for(state="visible", timeout=2_000)
        except PlaywrightTimeoutError as error:
            # An absent optional question is valid unless the input requests Yes.
            if has_part_time:
                message = "FBD did not expose its part-time occupation question"
                raise RuntimeError(message) from error
        else:
            await select_boolean(page, "employedPartTime", has_part_time)
            if has_part_time:
                await select_autocomplete(
                    page,
                    "secondaryOccupation",
                    data["part_time_occupation"],
                )

    await fill_text(page, "emailAddress", data["email"])
    # The mobile prefix is a dropdown; the remaining seven digits are a text input.
    prefix, remaining = split_mobile_phone(data["phone"])
    phone_group = form_group(page, "irishPhoneNumber")
    await select_responsive_dropdown(phone_group, prefix)
    await phone_group.locator("#mobileInput").fill(remaining)
    # Move focus so phone-number validation completes before the next radio click.
    await phone_group.locator("#mobileInput").press("Tab")
    await select_radio(page, "spousePartnerAssumption", "You or your Spouse/Partner")

    # Marketing consent is optional and must match the input data explicitly.
    marketing = form_group(page, "consentMarketing").locator('input[type="checkbox"]')
    if data.get("marketing_consent", False):
        await marketing.check(force=True)
    elif await marketing.is_checked():
        # Clear a preselected checkbox so reruns remain deterministic.
        await marketing.uncheck(force=True)
    print("Completed FBD About You")


async def fill_car_details(page, data):
    """Complete the supported registered-car happy path."""
    # This accordion becomes available only after About You is fully valid.
    await open_accordion(page, "car-details-panel")
    registration = page.locator("fbd-form-group--car-reg-lookup")
    # Registration lookup expects compact uppercase text such as 12D12345.
    await registration.locator("#regNoInput").fill(
        normalize_registration(data["car_registration"])
    )
    await registration.get_by_role(
        "button", name=re.compile(r"Find\s*Vehicle", re.IGNORECASE)
    ).click()
    # Dependent car questions are not inserted until the lookup has completed.
    await registration.locator(".vehicle-confirmation-container").wait_for(
        state="visible", timeout=20_000
    )
    # The current path assumes the lookup result belongs to the requested vehicle.
    await select_boolean(page, "isThisYourCar", True)

    await fill_text(page, "car-details-vehicle-value", data["car_value"])
    # Convert the shared canonical owner value to FBD's visible wording.
    owner = FBD_MAPPINGS["registered_owner"][data["registered_owner"]]
    await select_dropdown(page, "car-details-registered-owner", owner)
    await select_boolean(
        page,
        "car-details-iscarrighthanddrive",
        data.get("right_hand_drive", True),
    )

    await form_group(page, "car-details-was-reg-outside").wait_for(
        state="visible", timeout=10_000
    )
    # FBD inserts this question after the right-hand-drive answer is accepted.
    await select_boolean(
        page,
        "car-details-was-reg-outside",
        data.get("registered_outside_ireland_uk", False),
    )

    await form_group(page, "vehiclePurchaseDate").wait_for(
        state="visible", timeout=10_000
    )
    await select_month_year(page, "vehiclePurchaseDate", data["car_purchase_date"])

    # Shared quote data uses stable keys; the site-facing text lives in mappings.
    usage = FBD_MAPPINGS["car_usage"][data.get("car_usage", "social")]
    await select_radio(page, "car-details-use", usage)
    if data.get("car_has_modifications", False):
        # Modification details vary by modification type and need their own mapping.
        raise NotImplementedError("FBD modified-car details are not yet supported")
    await select_boolean(page, "car-details-has-modifications", False)
    print("Completed FBD About Your Car")


async def fill_driving_history(page, data):
    """Complete FBD's supported full-Irish-licence history path."""
    await open_accordion(page, "driver-history-panel")
    # Stop explicitly where the form would require detail screens not yet mapped.
    if data["licence_type"] != "full":
        raise NotImplementedError("FBD currently supports a full Irish licence only")
    await select_radio(page, "licence-type", FBD_MAPPINGS["licence_type"]["full"])
    await select_year_count(
        page,
        "years-as-full-irish-licence-holder",
        data["licence_duration"],
    )
    if data.get("has_penalty_points", False):
        # Do not silently answer No when the shared input contains risk information.
        raise NotImplementedError("FBD penalty-point details are not yet supported")
    await select_boolean(page, "driver-penalty-points", False)
    if data.get("has_claims", False):
        # Claim dates, types, and amounts require a repeatable claim-detail flow.
        raise NotImplementedError("FBD claims are not yet supported")
    await select_boolean(page, "hasClaims", False)
    print("Completed FBD Your Driving History")


async def fill_additional_drivers(page, data):
    """Complete FBD's single-driver path."""
    await open_accordion(page, "additional-drivers-panel")
    # Named-driver detail fields need a separate mapped sub-journey.
    if data.get("add_additional_driver", False):
        raise NotImplementedError("FBD additional drivers are not yet supported")
    # Explicitly choose No rather than relying on an empty/default form state.
    await select_boolean(page, "additional-drivers-do-you-want-to-add-drivers", False)
    print("Completed FBD Additional Drivers")


async def fill_underwriting(page, data):
    """Answer FBD's supported no-risk underwriting path."""
    await open_accordion(page, "underwriting-panel")
    # Map FBD field identifiers to the provider-neutral keys in PERSONAL_INFO.
    questions = {
        "hasBeenEverDisqualified": "has_disqualification",
        "hasBeenEverBeenCovictedCriminalOffence": "has_pending_convictions",
        "hasSpecialMedicalOrPhysicalCondition": "has_medical_condition",
        "hasInsuranceCancelled": "has_insurance_cancelled",
    }
    for question_key, data_key in questions.items():
        # A Yes answer exposes follow-up details that are not yet automated.
        if data.get(data_key, False):
            raise NotImplementedError(f"FBD '{data_key}' details are not yet supported")
        # Each response is selected independently so Angular validates every question.
        await select_boolean(page, question_key, False)
    print("Completed FBD underwriting questions")


async def fill_discounts(page, data):
    """Complete FBD's NCD and household-policy discount questions."""
    await open_accordion(page, "discounts-panel")
    ncd_years = int(data.get("no_claims_discount", 0))
    # FBD represents NCD duration as a radio band rather than a free-form number.
    await select_year_count(page, "no-claims-discount-type", ncd_years)

    # Country, insurer, and expiry are conditional on having an existing NCD.
    if ncd_years:
        country = FBD_MAPPINGS["ncd_country"][
            data.get("country_of_most_recent_ncd", "ireland")
        ]
        await select_radio(page, "ncd-earned-location-type", country)
        await select_autocomplete(
            page,
            "current-insurer-type",
            data["previous_insurer"],
            exact=False,
        )
        # The expiry component accepts month and year, not the original full date.
        await select_month_year(
            page,
            "discounts-ncd-expiry",
            data["current_policy_end_date"],
        )

    await select_boolean(
        page,
        "any-fbd-customer-in-household",
        data.get("existing_fbd_household_policy", False),
    )
    print("Completed FBD Your Discounts")


async def fill_your_details(page, data):
    """Complete every supported accordion on FBD's first quote page."""
    # Preserve page order because each completed panel unlocks the next panel.
    await fill_about_you(page, data)
    await fill_car_details(page, data)
    await fill_driving_history(page, data)
    await fill_additional_drivers(page, data)
    await fill_underwriting(page, data)
    await fill_discounts(page, data)


async def run(playwright: Playwright, data):
    """Complete the supported portion of FBD's Your Details page."""
    # Keep the browser headed while developing so failed conditional steps are visible.
    browser = await playwright.chromium.launch(headless=False)
    try:
        # Irish locale and Dublin time keep date parsing aligned with FBD's journey.
        page = await browser.new_page(locale="en-IE", timezone_id="Europe/Dublin")
        await open_quote_form(page)
        await fill_your_details(page, data)
        print("Completed the supported FBD Your Details journey")
    finally:
        # Always release Chromium, including when an intermediate locator fails.
        await browser.close()


def supported_mappings():
    """Return FBD mappings that have been verified against the live form."""
    return tuple(FBD_MAPPINGS)


async def main(data):
    """Run FBD as a standalone provider."""
    async with async_playwright() as playwright:
        await run(playwright, data)
