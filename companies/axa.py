import asyncio
from playwright.async_api import Playwright, async_playwright
from data_maps.axa import AXA_MAPPINGS
import helper_functions.axa as axa_helpers
from datetime import datetime
import random


PROFILES = [
    {
        "name": "chrome_win_uk",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.110 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080},
        "screen": {"width": 1920, "height": 1080},
        "locale": "en-GB",
        "timezone": "Europe/London",
        "accept_language": "en-GB,en;q=0.9",
        "sec_ch_ua": '"Chromium";v="120", "Not;A=Brand";v="99"',
        "platform": '"Windows"'
    },
    {
        "name": "chrome_win_us",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.110 Safari/537.36",
        "viewport": {"width": 1366, "height": 768},
        "screen": {"width": 1366, "height": 768},
        "locale": "en-US",
        "timezone": "America/New_York",
        "accept_language": "en-US,en;q=0.9",
        "sec_ch_ua": '"Chromium";v="120", "Not;A=Brand";v="99"',
        "platform": '"Windows"'
    }
]


async def accept_cookies(page):
    """Accept cookies if the banner appears"""
    try:
        # Look for common cookie acceptance buttons
        cookie_selectors = [
            'button:has-text("Accept All")',
            'button:has-text("Accept")',
            'button:has-text("I agree")',
            '#onetrust-accept-btn-handler',
            '.cookie-accept',
            '[data-testid="cookie-accept"]'
        ]
        
        for selector in cookie_selectors:
            try:
                await page.locator(selector).first.click(timeout=3000)
                print("Clicked cookie acceptance button")
                return
            except:
                continue
        print("No cookie banner found")
    except:
        print("Cookie acceptance failed")


async def fill_vehicle_details(page, data):
    """Fill vehicle details section"""
    print("\n--- Filling Vehicle Details Section ---")
    vehicle_section = page.locator('section[id="VehicleDetails"]')
    await vehicle_section.wait_for(state="visible")
    
    # Registration number
    try:
        registration_input = vehicle_section.locator(
            'input[name="VehicleDetails.VehicleRegistrationNumber"]'
        )
        await registration_input.fill(data['car_registration'])
        print(f"Filled registration number: {data['car_registration']}")
        
        # Click Find car button
        await vehicle_section.get_by_role("button", name="Find car", exact=True).click()
        print("Clicked 'Find car' button")

        # AXA adds this confirmation field after a successful registration lookup.
        confirm_car_yes = vehicle_section.locator(
            'label[for="VehicleDetails.ConfirmCarSearchBtn1"]'
        )
        await confirm_car_yes.wait_for(state="visible")
        await confirm_car_yes.click()
        print("Confirmed the registration lookup returned the correct car")
    except Exception as e:
        print(f"Error filling vehicle registration: {e}")
    
    # Business use
    try:
        business_use = data.get("business_use", False)
        business_use_value = AXA_MAPPINGS["business_use"][business_use]
        option_id = 1 if business_use else 2
        business_use_label = vehicle_section.locator(
            f'label[for="VehicleDetails.IsVehicleForBusinessUse{option_id}"]'
        )
        await business_use_label.wait_for(state="visible")
        await business_use_label.click()
        print(f"Selected business use: {business_use_value}")
    except Exception as e:
        print(f"Error selecting business use: {e}")

    if business_use:
        try:
            cover_type = data.get("business_use_cover", "limited_business")
            cover_value = AXA_MAPPINGS["business_use_cover"][cover_type]
            cover_input = vehicle_section.locator(
                f'input[name="VehicleDetails.VehicleClassOfUseTypeId"]'
                f'[value="{cover_value}"]'
            )
            await cover_input.wait_for(state="attached")
            cover_option_id = await cover_input.get_attribute("id")
            cover_label = vehicle_section.locator(
                f'label[for="{cover_option_id}"]'
            )
            await cover_label.wait_for(state="visible")
            await cover_label.click()
            print(f"Selected business use cover: {cover_type}")
        except Exception as e:
            print(f"Error selecting business use cover: {e}")

    # AXA asks about commuting after business use is set to No.
    else:
        try:
            commuting_use = data.get("commuting_use", False)
            option_id = 1 if commuting_use else 2
            commuting_use_label = vehicle_section.locator(
                f'label[for="VehicleDetails.IsVehicleForCommutingUse{option_id}"]'
            )
            await commuting_use_label.wait_for(state="visible")
            await commuting_use_label.click()
            print(f"Selected commuting use: {commuting_use}")
        except Exception as e:
            print(f"Error selecting commuting use: {e}")
    
    # Annual distance
    try:
        distance_category = axa_helpers.map_annual_distance(data.get('estimated_mileage', 10000))
        distance_value = AXA_MAPPINGS["annual_distance"][distance_category]
        await vehicle_section.locator(
            'select[name="VehicleDetails.AnnualDistanceDrivenTypeId"]'
        ).select_option(value=distance_value)
        print(f"Selected annual distance: {distance_category}")
    except Exception as e:
        print(f"Error selecting annual distance: {e}")


async def fill_personal_details(page, data):
    """Fill personal details section"""
    print("\n--- Filling Personal Details Section ---")
    personal_section = page.locator('section[id="ProposerDetails"]')
    await personal_section.wait_for(state="visible")

    async def click_radio_label(field_name, value):
        radio_input = personal_section.locator(
            f'input[name="{field_name}"][value="{value}"]'
        )
        await radio_input.wait_for(state="attached")
        option_id = await radio_input.get_attribute("id")
        option_label = personal_section.locator(f'label[for="{option_id}"]')
        await option_label.wait_for(state="visible")
        await option_label.click()

    # Title
    try:
        title_value = AXA_MAPPINGS["title"][data['title']]
        await click_radio_label("ProposerDetails.TitleTypeId", title_value)
        print(f"Selected title: {data['title']}")
    except Exception as e:
        print(f"Error selecting title: {e}")
    
    # First name
    try:
        await personal_section.locator(
            'input[name="ProposerDetails.FirstName"]'
        ).fill(data['first_name'])
        print(f"Filled first name: {data['first_name']}")
    except Exception as e:
        print(f"Error filling first name: {e}")
    
    # Last name
    try:
        await personal_section.locator(
            'input[name="ProposerDetails.LastName"]'
        ).fill(data['last_name'])
        print(f"Filled last name: {data['last_name']}")
    except Exception as e:
        print(f"Error filling last name: {e}")
    
    # Date of birth
    try:
        date_components = axa_helpers.split_date_components(data['date_of_birth'])
        await personal_section.locator(
            'input[name="ProposerDetails.DateOfBirth.Day"]'
        ).fill(date_components['day'])
        await personal_section.locator(
            'input[name="ProposerDetails.DateOfBirth.Month"]'
        ).fill(date_components['month'])
        await personal_section.locator(
            'input[name="ProposerDetails.DateOfBirth.Year"]'
        ).fill(date_components['year'])
        print(f"Filled date of birth: {data['date_of_birth']}")
    except Exception as e:
        print(f"Error filling date of birth: {e}")
    
    # Email
    try:
        await personal_section.locator(
            'input[name="ProposerDetails.EmailAddress"]'
        ).fill(data['email'])
        print(f"Filled email: {data['email']}")
    except Exception as e:
        print(f"Error filling email: {e}")
    
    # Phone number
    try:
        formatted_phone = axa_helpers.format_phone_number(data['phone'])
        await personal_section.locator('input[name="phone-number"]').fill(formatted_phone)
        print(f"Filled phone number: {formatted_phone}")
    except Exception as e:
        print(f"Error filling phone number: {e}")
    
    # Employment status
    try:
        employment_status = axa_helpers.map_employment_status(data.get('occupation', 'employed'))
        employment_value = AXA_MAPPINGS["employment_status"][employment_status]
        await click_radio_label(
            "ProposerDetails.EmploymentStatusTypeId", employment_value
        )
        print(f"Selected employment status: {employment_status}")
    except Exception as e:
        print(f"Error selecting employment status: {e}")

    # AXA renders the occupation search dynamically for applicable statuses.
    try:
        occupation_input = personal_section.locator(
            'input[name*="Occupation"]:not([type="radio"]), '
            'input[placeholder*="occupation" i]'
        ).first
        await occupation_input.wait_for(state="visible", timeout=3_000)
        await occupation_input.fill(data['occupation'])
        print(f"Filled occupation search: {data['occupation']}")

        occupation_suggestion = personal_section.locator(
            '.react-autosuggest__suggestion, [role="option"]'
        ).first
        await occupation_suggestion.wait_for(state="visible", timeout=5_000)
        await occupation_suggestion.click()
        print("Selected occupation from suggestions")
    except Exception as e:
        print(f"Occupation field was not shown or selectable: {e}")

    # Part-time occupation
    try:
        part_time_occupation = data.get("part_time_occupation", False)
        part_time_value = "true" if part_time_occupation else "false"
        part_time_input = personal_section.locator(
            'input[name="ProposerDetails.PartTimeOccupation"]'
            f'[value="{part_time_value}"]'
        )
        try:
            await part_time_input.wait_for(state="attached", timeout=3_000)
        except Exception:
            print("Part-time occupation question was not shown; skipping it")
        else:
            option_id = await part_time_input.get_attribute("id")
            option_label = personal_section.locator(f'label[for="{option_id}"]')
            await option_label.wait_for(state="visible", timeout=3_000)
            await option_label.click()
            print(f"Selected part-time occupation: {part_time_occupation}")
    except Exception as e:
        print(f"Error selecting part-time occupation: {e}")
    
    # Address
    try:
        address = data['address']
        address_query = address.get('postal_code') or (
            f"{address['street']}, {address['city']}, {address['county']}"
        )
        await personal_section.locator(
            'input[name="ProposerDetails.AddressDisplayFormatted"]'
        ).fill(address_query)
        print(f"Filled address search: {address_query}")

        try:
            address_suggestion = personal_section.locator(
                '.react-autosuggest__suggestion, [role="option"]'
            ).first
            await address_suggestion.wait_for(state="visible", timeout=5_000)
            await address_suggestion.click()
            print("Selected address from suggestions")
        except Exception as e:
            print(f"No address suggestion could be selected: {e}")
    except Exception as e:
        print(f"Error filling address: {e}")
    
    # Household type
    try:
        household_type = data.get("household_type", "owned")
        household_value = AXA_MAPPINGS["household_type"][household_type]
        await click_radio_label("ProposerDetails.HouseHoldTypeId", household_value)
        print(f"Selected household type: {household_type}")
    except Exception as e:
        print(f"Error selecting household type: {e}")


async def fill_driving_history(page, data):
    """Fill driving history section"""
    print("\n--- Filling Driving History Section ---")
    driving_section = page.locator('section[id="DrivingHistory"]')
    await driving_section.wait_for(state="visible")

    async def click_radio_label(field_name, value):
        radio_input = driving_section.locator(
            f'input[name="{field_name}"][value="{value}"]'
        )
        await radio_input.wait_for(state="attached")
        option_id = await radio_input.get_attribute("id")
        option_label = driving_section.locator(f'label[for="{option_id}"]')
        await option_label.wait_for(state="visible")
        await option_label.click()

    # Driving licence type
    try:
        licence_type = axa_helpers.map_licence_type(data['licence_type'], data['licence_duration'])
        licence_value = AXA_MAPPINGS["licence_type"][licence_type]
        await click_radio_label(
            "DrivingHistory.DrivingLicenceTypeId", licence_value
        )
        print(f"Selected licence type: {licence_type}")
    except Exception as e:
        print(f"Error selecting licence type: {e}")
    
    # Years licence held
    try:
        years_category = axa_helpers.map_years_licence_held(data['licence_duration'])
        years_value = AXA_MAPPINGS["years_licence_held"][years_category]
        await driving_section.locator(
            'select[name="DrivingHistory.YearsLicenceHeldTypeId"]'
        ).select_option(value=years_value)
        print(f"Selected years licence held: {years_category}")
    except Exception as e:
        print(f"Error selecting years licence held: {e}")
    
    # Penalty points
    try:
        has_penalty_points = data.get('has_penalty_points', False)
        penalty_value = AXA_MAPPINGS["penalty_points"][has_penalty_points]
        await click_radio_label(
            "DrivingHistory.PenaltyPointsDetails.HasPenaltyPoints",
            penalty_value,
        )
        print(f"Selected penalty points: {penalty_value}")
    except Exception as e:
        print(f"Error selecting penalty points: {e}")
    
    # Driving experience
    experience = None
    try:
        experience = axa_helpers.map_driving_experience(data['driving_experience'])
        experience_value = AXA_MAPPINGS["driving_experience"][experience]
        await click_radio_label(
            "DrivingHistory.DrivingExperienceTypeId", experience_value
        )
        print(f"Selected driving experience: {experience}")
    except Exception as e:
        print(f"Error selecting driving experience: {e}")

    async def select_no_claims_years(field_name, years):
        years = max(0, min(int(years), 10))
        option_value = AXA_MAPPINGS["no_claims_discount_years"][years]
        await driving_section.locator(
            f'select[name="{field_name}"]'
        ).select_option(value=option_value)
        return "10+" if years == 10 else years

    # AXA asks for NCD years after "Insured in own name" is selected.
    if experience == "own_name":
        try:
            display_years = await select_no_claims_years(
                "DrivingHistory.NoClaimsDiscountYearsInOwnNameTypeId",
                data.get("no_claims_discount", 0),
            )
            print(f"Selected no claims discount years: {display_years}")
        except Exception as e:
            print(f"Error selecting no claims discount years: {e}")

    # AXA may ask for named-driver years after either own-name or named-driver
    # experience is selected. For own-name experience this is additional to NCD.
    if experience in {"own_name", "named_driver"}:
        try:
            named_driver_field = driving_section.locator(
                'select[name="DrivingHistory.NoClaimDiscountYearsAsNamedDriverTypeId"]'
            )
            await named_driver_field.wait_for(state="visible", timeout=3_000)
            default_named_driver_years = (
                data.get("no_claims_discount", 0)
                if experience == "named_driver"
                else 0
            )
            display_years = await select_no_claims_years(
                "DrivingHistory.NoClaimDiscountYearsAsNamedDriverTypeId",
                data.get(
                    "named_driver_no_claims_discount",
                    default_named_driver_years,
                ),
            )
            print(f"Selected named-driver years: {display_years}")
        except Exception as e:
            print(f"Named-driver years question was not shown or selectable: {e}")

    # Some combinations require confirmation of the combined consecutive years.
    if experience in {"own_name", "named_driver"}:
        try:
            claims_total_checkbox = driving_section.locator(
                'input[name="DrivingHistory.IsClaimsFreeTotalConfirmed"]'
            )
            await claims_total_checkbox.wait_for(state="attached", timeout=3_000)
            claims_total_label = driving_section.locator(
                'label[for="DrivingHistory.IsClaimsFreeTotalConfirmed"]'
            )
            await claims_total_label.wait_for(state="visible", timeout=3_000)
            await claims_total_label.click()
            print("Confirmed the combined claims-free driving experience")
        except Exception:
            print("Combined claims-free confirmation was not shown; skipping it")


async def fill_claims_history(page, data):
    """Fill claims history section"""
    print("\n--- Filling Claims History Section ---")
    claims_section = page.locator('section[id="ClaimsHistory"]')
    await claims_section.wait_for(state="visible")

    try:
        has_previous_claims = data.get("has_previous_claims", False)
        claims_value = "true" if has_previous_claims else "false"
        claims_input = claims_section.locator(
            f'input[name="HasPreviousClaims"][value="{claims_value}"]'
        )
        await claims_input.wait_for(state="attached")
        await claims_input.evaluate("element => element.click()")
        if not await claims_input.is_checked():
            raise RuntimeError("AXA did not register the claims selection")
        print(f"Selected previous claims: {has_previous_claims}")
    except Exception as e:
        print(f"Error selecting previous claims: {e}")


async def fill_discounts(page, data):
    """Fill discounts section"""
    print("\n--- Filling Discounts Section ---")
    discounts_section = page.locator('section[id="Discounts"]')
    await discounts_section.wait_for(state="visible")

    try:
        has_multi_policy_discount = data.get("multi_policy_discount", False)
        discount_value = "true" if has_multi_policy_discount else "false"
        discount_input = discounts_section.locator(
            'input[name="CoverDetails.HasMultiProductDiscount"]'
            f'[value="{discount_value}"]'
        )
        await discount_input.wait_for(state="attached")
        await discount_input.evaluate("element => element.click()")
        if not await discount_input.is_checked():
            raise RuntimeError("AXA did not register the multi-policy selection")
        print(f"Selected multi-policy discount: {has_multi_policy_discount}")
    except Exception as e:
        print(f"Error selecting multi-policy discount: {e}")


async def fill_cover_details(page, data):
    """Fill cover details section"""
    print("\n--- Filling Cover Details Section ---")
    cover_section = page.locator('section[id="YourCover"]')
    await cover_section.wait_for(state="visible")

    async def set_checkbox(field_name, desired_state):
        checkbox = cover_section.locator(f'input[name="{field_name}"]')
        await checkbox.wait_for(state="attached")
        if await checkbox.is_checked() != desired_state:
            await checkbox.evaluate("element => element.click()")
        if await checkbox.is_checked() != desired_state:
            raise RuntimeError(f"AXA did not update {field_name}")

    # Cover start date
    try:
        formatted_date = axa_helpers.format_date_for_axa(data['policy_start_date'])
        await cover_section.locator(
            'input[name="CoverDetails.CoverStartDate"]'
        ).fill(formatted_date)
        print(f"Filled cover start date: {formatted_date}")
    except Exception as e:
        print(f"Error filling cover start date: {e}")
    
    # Accept assumptions
    try:
        accept_assumptions = data.get('accept_terms', True)
        await set_checkbox("ConfirmAssumptions", accept_assumptions)
        print(f"Set assumptions acceptance: {accept_assumptions}")
    except Exception as e:
        print(f"Error checking assumptions: {e}")
    
    # Marketing consent (optional)
    try:
        marketing_consent = data.get('marketing_consent', False)
        await set_checkbox(
            "CoverDetails.IsGdprConsentGiven", marketing_consent
        )
        print(f"Set marketing consent: {marketing_consent}")
    except Exception as e:
        print(f"Error checking marketing consent: {e}")
    
    # Data consent
    try:
        data_consent = data.get('data_consent', True)
        consent_value = AXA_MAPPINGS["data_consent"][data_consent]
        consent_input = cover_section.locator(
            'input[name="CoverDetails.IsDataConsentGiven"]'
            f'[value="{consent_value}"]'
        )
        await consent_input.wait_for(state="attached")
        await consent_input.evaluate("element => element.click()")
        if not await consent_input.is_checked():
            raise RuntimeError("AXA did not register the data-consent selection")
        print(f"Selected data consent: {consent_value}")
    except Exception as e:
        print(f"Error selecting data consent: {e}")

    # AXA conditionally offers a phone call if the customer has questions.
    try:
        phone_consent = data.get('phone_consent', True)
        phone_consent_value = AXA_MAPPINGS["phone_consent"][phone_consent]
        phone_consent_input = cover_section.locator(
            'input[name="CoverDetails.IsPhoneConsentGiven"]'
            f'[value="{phone_consent_value}"]'
        )
        await phone_consent_input.wait_for(state="attached", timeout=3_000)
        await phone_consent_input.evaluate("element => element.click()")
        if not await phone_consent_input.is_checked():
            raise RuntimeError("AXA did not register the phone-help selection")
        print(f"Selected phone help consent: {phone_consent}")
    except Exception as e:
        print(f"Phone help question was not shown or selectable: {e}")


async def submit_quote(page):
    """Submit the completed AXA quote form."""
    cover_section = page.locator('section[id="YourCover"]')
    get_quote_button = cover_section.locator('button[name="getquote-btn"]')
    await get_quote_button.wait_for(state="visible")
    await get_quote_button.click()
    print("Clicked 'Get a Quote'")


async def extract_quotes(page, data):
    """Extract quote information and store results"""
    print("\n--- Extracting Quote Information ---")
    
    results = []
    
    try:
        # Wait for quote results to load
        await asyncio.sleep(10)
        
        # Look for price elements
        price_selectors = [
            '[data-testid="price"]',
            '.price',
            '.quote-price',
            '[class*="price"]',
            '[id*="price"]'
        ]
        
        price_found = False
        for selector in price_selectors:
            try:
                price_element = page.locator(selector).first
                if await price_element.count() > 0:
                    price_text = await price_element.inner_text()
                    if any(char.isdigit() for char in price_text):
                        print(f"Found price: {price_text}")
                        results.append(f"Comprehensive: {price_text}")
                        price_found = True
                        break
            except:
                continue
        
        if not price_found:
            print("No price found with standard selectors")
            # Try to find any element containing Euro symbol or numbers
            page_content = await page.content()
            if "EUR" in page_content or "EUR" in page_content:
                results.append("Comprehensive: Price found on page (could not extract exact value)")
            else:
                results.append("Comprehensive: Price not found")
        
    except Exception as e:
        print(f"Error extracting quotes: {e}")
        results.append("Comprehensive: Extraction failed")
    
    # Store results in file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("insurance_quotes.txt", "a") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Company: AXA Insurance\n")
        f.write(f"Quote Generated: {timestamp}\n")
        f.write(f"Personal Details: {data['first_name']} {data['last_name']}\n")
        f.write(f"Vehicle: {data['car_registration']}\n")
        f.write(f"{'='*50}\n")
        for result in results:
            f.write(f"{result}\n")
        f.write(f"{'='*50}\n\n")
    
    print(f"AXA results saved to insurance_quotes.txt")

page = None
async def run(playwright: Playwright, data):
    """Main automation function for AXA"""
    # browser = await playwright.chromium.launch(headless=False, proxy=None)
    # context = await browser.new_context(
    #     viewport={"width": 1366, "height": 768},
    #     locale="en-IE",
    #     timezone_id="Europe/Dublin",
    #     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    # )
    # page = await context.new_page()
    profile = random.choice(PROFILES)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # switch to False if you can afford it
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = await browser.new_context(
            user_agent=profile["user_agent"],
            viewport=profile["viewport"],
            screen=profile["screen"],
            locale=profile["locale"],
            timezone_id=profile["timezone"],
            device_scale_factor=1
        )

        # Basic stealth patch (minimal but safer than fake-heavy hacks)
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-GB', 'en']
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3]
            });

            window.chrome = {
                runtime: {}
            };
        """)

        page = await context.new_page()

        await page.set_extra_http_headers({
            "accept-language": profile["accept_language"],
            "sec-ch-ua": profile["sec_ch_ua"],
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": profile["platform"]
        })
        await page.goto("https://www.axa.ie/car-insurance/")
        await asyncio.sleep(5)





    
    # try:
    #     # Navigate to AXA insurance quote page
    #     print("Attempting to navigate to AXA car insurance page...")
    #     try:
    #         await page.goto("https://www.axa.ie/car-insurance/", wait_until="networkidle")
    #         print("Successfully navigated to AXA car insurance page")
    #     except Exception as e:
    #         print(f"Failed to navigate to direct quote page: {e}")
    #         print("Trying main page first...")
    #         await page.goto("https://www.axa.ie/car-insurance/", timeout=30000)
    #         await asyncio.sleep(3)
        
    #     # Check if we got blocked
        
    #     # Get quote price from user
    #     quote_price = input("Enter AXA quote price (or press Enter to skip): ").strip()
        
    #     # Store results
    #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     with open("insurance_quotes.txt", "a") as f:
    #         f.write(f"\n{'='*50}\n")
    #         f.write(f"Company: AXA Insurance\n")
    #         f.write(f"Quote Generated: {timestamp}\n")
    #         f.write(f"Personal Details: {data['first_name']} {data['last_name']}\n")
    #         f.write(f"Vehicle: {data['car_registration']}\n")
    #         f.write(f"{'='*50}\n")
    #         if quote_price:
    #             f.write(f"Comprehensive: {quote_price}\n")
    #             print(f"AXA quote price saved: {quote_price}")
    #         else:
    #             f.write("Status: Quote not completed manually\n")
    #             print("AXA quote skipped")
    #         f.write(f"{'='*50}\n\n")
        
    #     print("\nAXA processing complete. Browser will close in 30 seconds...")
    #     print("Or press Ctrl+C to close immediately.")
    #     await asyncio.sleep(30)
        
    # except Exception as e:
    #     print(f"Error opening AXA page: {e}")
        
    #     # Store error message
    #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     with open("insurance_quotes.txt", "a") as f:
    #         f.write(f"\n{'='*50}\n")
    #         f.write(f"Company: AXA Insurance\n")
    #         f.write(f"Quote Generated: {timestamp}\n")
    #         f.write(f"Personal Details: {data['first_name']} {data['last_name']}\n")
    #         f.write(f"Vehicle: {data['car_registration']}\n")
    #         f.write(f"{'='*50}\n")
    #         f.write("Status: Manual quote assistance failed\n")
    #         f.write(f"Error: {e}\n")
    #         f.write(f"{'='*50}\n\n")
    
    # finally:
    #     await browser.close()


async def main(data):
    """Main entry point for AXA automation"""
    async with async_playwright() as playwright:
        await run(playwright, data)
