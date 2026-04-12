import asyncio
from playwright.async_api import Playwright, async_playwright
from data_maps.an_post import AN_POST_MAPPINGS
from helper_functions.an_post import format_mileage, calculate_no_claims_discount
import helper_functions.general as general_helpers
from datetime import datetime


async def accept_cookies(page):
    """Accept cookies if the banner appears"""
    try:
        await page.locator('#onetrust-accept-btn-handler').click(timeout=5000)
        print("Clicked 'Accept All' for cookies")
    except:
        print("Cookie banner not found or already accepted")


async def select_title(page, title):
    """Select title (Mr/Mrs/Ms)"""
    await page.locator(f'div[role="button"][aria-labelledby="{title}"]').first.click()
    print(f"Selected title: {title}")


async def fill_first_name(page, name):
    """Fill first name field"""
    await page.locator('input[placeholder="First Name"]').fill(name)
    print(f"Filled first name with: {name}")


async def fill_last_name(page, name):
    """Fill last name field"""
    await page.locator('input[placeholder="Last Name"]').fill(name)
    print(f"Filled last name with: {name}")


async def fill_date_of_birth(page, date_string):
    """Fill date of birth fields (DD/MM/YYYY)"""
    date_obj = datetime.strptime(date_string, "%d-%m-%Y")
    
    await page.locator('input[placeholder="DD"]').first.fill(str(date_obj.day).zfill(2))
    await page.locator('input[placeholder="MM"]').first.fill(str(date_obj.month).zfill(2))
    await page.locator('input[placeholder="YYYY"]').first.fill(str(date_obj.year))
    print(f"Filled date of birth: {date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year}")


async def fill_phone_number(page, phone):
    """Fill phone number field"""
    await page.locator('input[placeholder="Mobile Number"]').fill(general_helpers.format_phone(phone))
    print(f"Filled phone number with: {phone}")


async def fill_email(page, email):
    """Fill email field"""
    await page.locator('input[placeholder="Email"]').fill(email)
    print(f"Filled email with: {email}")


async def fill_occupation(page, occupation):
    """Fill occupation with autocomplete"""
    occupation_input = page.locator('input[placeholder="Begin typing..."]')
    await occupation_input.fill(occupation[:3])
    await asyncio.sleep(1.5)
    
    # Wait for dropdown and select first option
    await page.locator('.p-autocomplete-panel .p-autocomplete-item').first.click()
    print(f"Selected occupation: {occupation}")


async def fill_postcode(page, postcode):
    """Fill address/Eircode with autocomplete"""
    address_input = page.locator('input[placeholder="Start typing your Eircode or address"]')
    await address_input.fill(postcode)
    await asyncio.sleep(2)
    
    # Wait for dropdown and select first option
    try:
        await page.locator('.p-autocomplete-panel .p-autocomplete-item').first.click()
        print(f"Selected address for postcode: {postcode}")
    except:
        await address_input.press('Enter')
        print(f"Pressed Enter for postcode: {postcode}")


async def fill_car_registration(page, registration):
    """Fill car registration and search for vehicle"""
    await page.locator('input[placeholder="Car Registration Number"]').fill(registration)
    print(f"Filled car registration with: {registration}")
    
    # Click "Find your Vehicle" button
    await asyncio.sleep(1)
    await page.locator('button:has-text("Find your Vehicle")').click()
    print("Clicked 'Find your Vehicle' button")
    await asyncio.sleep(3)  # Wait for vehicle lookup


async def fill_car_value(page, value):
    """Fill car value field"""
    await page.locator('input[placeholder="Car Value"]').fill(str(value))
    print(f"Filled car value with: €{value}")


async def select_tile_option(page, question_text, option_label):
    """Generic function to select a tile option button"""
    # Find the question container by its label text
    container = page.locator(f'div.equote-question-base:has(span[data-cy="title"]:has-text("{question_text}"))')
    await container.locator(f'div[role="button"][aria-labelledby="{option_label}"]').click()
    print(f"Selected '{option_label}' for '{question_text}'")


async def select_boolean_option(page, question_text, value):
    """Select Yes/No boolean option"""
    container = page.locator(f'div.equote-question-base:has(span[data-cy="title"]:has-text("{question_text}"))')
    await container.locator(f'div[role="button"][aria-labelledby="{value}"]').click()
    print(f"Selected '{value}' for '{question_text}'")


async def select_dropdown_option(page, question_text, option_text):
    """Select option from PrimeNG dropdown"""
    container = page.locator(f'div.equote-question-base:has(span[data-cy="title"]:has-text("{question_text}"))')
    
    # Click to open dropdown
    await container.locator('p-dropdown').click()
    await asyncio.sleep(0.5)
    
    # Select the option
    await page.locator(f'.p-dropdown-panel .p-dropdown-item:has-text("{option_text}")').first.click()
    print(f"Selected '{option_text}' for '{question_text}'")


async def fill_date_field(page, question_text, date_string):
    """Fill a date field (DD/MM/YYYY) by question text"""
    date_obj = datetime.strptime(date_string, "%d-%m-%Y")
    
    container = page.locator(f'div.equote-question-base:has(span[data-cy="title"]:has-text("{question_text}"))')
    
    await container.locator('input[placeholder="DD"]').fill(str(date_obj.day).zfill(2))
    await container.locator('input[placeholder="MM"]').fill(str(date_obj.month).zfill(2))
    await container.locator('input[placeholder="YYYY"]').fill(str(date_obj.year))
    print(f"Filled date for '{question_text}': {date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year}")


async def click_checkbox(page, checkbox_text_contains):
    """Click a checkbox by partial label text"""
    container = page.locator(f'div.equote-question-base:has(span[data-cy="title"]:has-text("{checkbox_text_contains}"))')
    await container.locator('p-checkbox').click()
    print(f"Clicked checkbox containing: '{checkbox_text_contains}'")


async def run(playwright: Playwright, data):
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto("https://insurance.anpostinsurance.ie/v2/equote/motor/risk")
    
    # Accept cookies
    await accept_cookies(page)
    await asyncio.sleep(1)

    # ==================== YOUR DETAILS SECTION ====================
    print("\n--- Filling Your Details Section ---")
    
    await select_title(page, AN_POST_MAPPINGS["title"][data["title"]])
    await fill_first_name(page, data["first_name"])
    await fill_last_name(page, data["last_name"])
    await fill_date_of_birth(page, data["date_of_birth"])
    await fill_phone_number(page, data["phone"])
    await fill_email(page, data["email"])
    await fill_occupation(page, data["occupation"])

    # ==================== YOUR CAR SECTION ====================
    print("\n--- Filling Your Car Section ---")
    
    await fill_postcode(page, data["address"]["postal_code"])
    await asyncio.sleep(1)
    
    await fill_car_registration(page, data["car_registration"])
    await asyncio.sleep(2)
    
    await fill_car_value(page, data["car_value"])
    
    # Right/Left hand drive
    await select_tile_option(page, "Is the car right or left hand drive?", AN_POST_MAPPINGS["right_hand_drive"][data["right_hand_drive"]])
    
    # Registered in Ireland
    await select_boolean_option(page, "Is the car registered in Ireland?", AN_POST_MAPPINGS["registered_in_ireland"][data["registered_in_ireland"]])
    
    # Is imported
    await select_boolean_option(page, "Is the car imported from outside of the Republic of Ireland?", AN_POST_MAPPINGS["is_imported"][data["is_imported"]])
    
    # Car purchase date
    await fill_date_field(page, "When did you purchase the car?", data["car_purchase_date"])
    
    # Annual mileage dropdown
    await select_dropdown_option(page, "How many Kilometers will the car travel over the next 12 months?", format_mileage(data["estimated_mileage"]))
    
    # Registered owner dropdown
    await select_dropdown_option(page, "Who is the registered owner of the car?", AN_POST_MAPPINGS["registered_owner"][data["registered_owner"]])
    
    # Car usage
    await select_tile_option(page, "What is the car used for?", AN_POST_MAPPINGS["car_usage"][data["car_usage"]])

    # ==================== YOUR LICENCE SECTION ====================
    print("\n--- Filling Your Licence Section ---")
    
    # Licence type
    await select_tile_option(page, "What type of licence do you have?", AN_POST_MAPPINGS["licence_type"][data["licence_type"]])
    await asyncio.sleep(0.5)
    
    # Licence duration dropdown
    await select_dropdown_option(page, "How long have you had your licence for?", data["licence_duration"])
    
    # Penalty points
    await select_boolean_option(page, "Do you have any active penalty points?", AN_POST_MAPPINGS["has_penalty_points"][data["has_penalty_points"]])

    # ==================== INSURANCE COVER SECTION ====================
    print("\n--- Filling Insurance Cover Section ---")
    
    # Driving experience
    await select_tile_option(page, "What is  your driving experience level?", AN_POST_MAPPINGS["driving_experience"][data["driving_experience"]])
    await asyncio.sleep(0.5)

    # Fill out No Claims Discount
    await select_dropdown_option(page, "How many consecutive years have you held a private car policy in your own name without an accident or claim?", calculate_no_claims_discount(data["no_claims_discount"]))
    await asyncio.sleep(0.5)

    # Fill out Country of most recent insurance
    await select_dropdown_option(page, "In what country was your most recent no claim discount earned?", general_helpers.capitalize_first_letter(data["country_of_most_recent_ncd"]))
    await asyncio.sleep(0.5)
    
    # Fill out Previous insurer
    await select_dropdown_option(page, "Who is your current/previous insurer?", general_helpers.capitalize_first_letter(data["previous_insurer"]))
    await asyncio.sleep(0.5)
    
    # Policy start date
    await fill_date_field(page, "When do you require cover from", data["policy_start_date"])

    # Is this the same date as current policy end date
    await select_boolean_option(page, "Is this the same as the end date of your existing policy", AN_POST_MAPPINGS["same_as_current_policy_end_date"][data["same_as_current_policy_end_date"]])
    
    # Payment type
    await select_tile_option(page, "How do you normally pay?", AN_POST_MAPPINGS["payment_type"][data["payment_type"]])

    # ==================== ADDITIONAL DRIVERS SECTION ====================
    print("\n--- Filling Additional Drivers Section ---")
    
    await select_boolean_option(page, "Would you like to add an additional driver?", AN_POST_MAPPINGS["add_additional_driver"][data["add_additional_driver"]])

    # ==================== KEEP IN CONTACT SECTION ====================
    print("\n--- Filling Keep In Contact Section ---")
    
    await select_boolean_option(page, "From time to time we would like to contact you", AN_POST_MAPPINGS["marketing_consent"][data["marketing_consent"]])

    await select_boolean_option(page, "Would you like to only receive details and/or special offers in relation to our Car Insurance by Email, SMS, Post or Phone? Is this ok? (You can withdraw consent at any time.)", AN_POST_MAPPINGS["marketing_consent"][data["marketing_consent"]])

    # ==================== TERMS AND CONDITIONS SECTION ====================
    print("\n--- Accepting Terms and Conditions ---")
    
    if AN_POST_MAPPINGS["accept_terms"][data["accept_terms"]]:
        await click_checkbox(page, "I confirm I have read and accept")

    # ==================== SUBMIT FORM ====================
    print("\n--- Form Complete ---")
    await asyncio.sleep(2)
    
    # Click the submit button
    await page.locator('button:has-text("Get an Indicative Price")').click()
    print("Clicked 'Get an Indicative Price' button")
    
    # Wait for results page to load
    await asyncio.sleep(15)
    
    # Extract and store initial price (Comprehensive)
    results = []
    
    try:
        initial_price_element = page.locator('#breadCrumb-Price')
        initial_price = await initial_price_element.inner_text()
        print(f"Initial Comprehensive Price: {initial_price}")
        results.append(f"Comprehensive: {initial_price}")
    except:
        print("Could not extract initial price")
        results.append("Comprehensive: Price not found")
    
    # Select Third Party Fire & Theft
    try:
        await page.locator('text=Third Party Fire And Theft').click()
        await asyncio.sleep(2)
        await page.locator('text=Recalculate').first.click()
        print("Selected 'Third Party Fire & Theft'")
        await asyncio.sleep(15)
        
        # Extract TPFT price
        tpft_price_element = page.locator('#breadCrumb-Price')
        tpft_price = await tpft_price_element.inner_text()
        print(f"Third Party Fire & Theft Price: {tpft_price}")
        results.append(f"Third Party Fire & Theft: {tpft_price}")
    except Exception as e:
        print("Could not select Third Party Fire & Theft or extract price")
        print(f"Exception: {e}")
        results.append("Third Party Fire & Theft: Price not found")
    
    
    # Store results in text file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("insurance_quotes.txt", "a") as f:
        f.write(f"Company: An Post Insurance\n")
        f.write(f"Quote Generated: {timestamp}\n")
        f.write(f"{'='*50}\n")
        for result in results:
            f.write(f"{result}\n")
        f.write(f"{'='*50}\n\n")
    
    print(f"\nResults saved to insurance_quotes.txt")
    
    # Keep browser open to see results
    await asyncio.sleep(10)
    await browser.close()


async def main(data):
    async with async_playwright() as playwright:
        await run(playwright, data)


