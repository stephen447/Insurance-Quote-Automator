import asyncio
from playwright.async_api import Playwright, async_playwright, expect

# Personal information dictionary
PERSONAL_INFO = {
    "title": "Mr",
    "first_name": "Stephen",
    "last_name": "Byrne",
    "email": "stephen.byrne@example.com",
    "phone": "0838128391",
    "date_of_birth": "1999-01-11",
    "occupation": "Software Developer",
    "car_registration": "12D12345",
    "car_value": "15000",
    "car_purchase_date": "2023-06-15",
    "estimated_mileage": "0 - 7500 (0km -12,000km)",
    "right_hand_drive": "Right",
    "registered_in_ireland": "Yes",
    "is_imported": "No",
    "registered_owner": "Proposer",
    "car_usage": "Social, domestic & pleasure use (including commuting)",
    "address": {
        "street": "123 Main Street",
        "city": "Dublin",
        "postal_code": "K36CF34",
        "country": "Ireland"
    },
    # Licence section
    "licence_type": "Full (Irish)",
    "licence_duration": "5",
    "has_penalty_points": "No",
    # Insurance Cover section
    "driving_experience": "Insured in my own name",
    "no_claims_discount": "4",
    "country_of_most_recent_ncd": "Ireland",
    "previous_insurer": "Allianz",
    "policy_start_date": "2026-05-01",
    "same_as_current_policy_end_date": "Yes",
    "payment_type": "In full",
    # Additional Drivers
    "add_additional_driver": "No",
    # Marketing
    "marketing_consent": "No",
    # Terms
    "accept_terms": True
}


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
    from datetime import datetime
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    
    # Get the DOB container specifically
    #dob_container = page.locator('#31f90f42-ad1f-f111-8138-005056853e6f-base')
    
    await page.locator('input[placeholder="DD"]').first.fill(str(date_obj.day).zfill(2))
    await page.locator('input[placeholder="MM"]').first.fill(str(date_obj.month).zfill(2))
    await page.locator('input[placeholder="YYYY"]').first.fill(str(date_obj.year))
    print(f"Filled date of birth: {date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year}")


async def fill_phone_number(page, phone):
    """Fill phone number field"""
    await page.locator('input[placeholder="Mobile Number"]').fill(phone)
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
    await page.locator('input[placeholder="Car Value"]').fill(value)
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
    from datetime import datetime
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    
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


async def run(playwright: Playwright):
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto("https://insurance.anpostinsurance.ie/v2/equote/motor/risk")
    
    # Accept cookies
    await accept_cookies(page)
    await asyncio.sleep(1)

    # ==================== YOUR DETAILS SECTION ====================
    print("\n--- Filling Your Details Section ---")
    
    await select_title(page, PERSONAL_INFO["title"])
    await fill_first_name(page, PERSONAL_INFO["first_name"])
    await fill_last_name(page, PERSONAL_INFO["last_name"])
    await fill_date_of_birth(page, PERSONAL_INFO["date_of_birth"])
    await fill_phone_number(page, PERSONAL_INFO["phone"])
    await fill_email(page, PERSONAL_INFO["email"])
    await fill_occupation(page, PERSONAL_INFO["occupation"])

    # ==================== YOUR CAR SECTION ====================
    print("\n--- Filling Your Car Section ---")
    
    await fill_postcode(page, PERSONAL_INFO["address"]["postal_code"])
    await asyncio.sleep(1)
    
    await fill_car_registration(page, PERSONAL_INFO["car_registration"])
    await asyncio.sleep(2)
    
    await fill_car_value(page, PERSONAL_INFO["car_value"])
    
    # Right/Left hand drive
    await select_tile_option(page, "Is the car right or left hand drive?", PERSONAL_INFO["right_hand_drive"])
    
    # Registered in Ireland
    await select_boolean_option(page, "Is the car registered in Ireland?", PERSONAL_INFO["registered_in_ireland"])
    
    # Is imported
    await select_boolean_option(page, "Is the car imported from outside of the Republic of Ireland?", PERSONAL_INFO["is_imported"])
    
    # Car purchase date
    await fill_date_field(page, "When did you purchase the car?", PERSONAL_INFO["car_purchase_date"])
    
    # Annual mileage dropdown
    await select_dropdown_option(page, "How many Kilometers will the car travel over the next 12 months?", PERSONAL_INFO["estimated_mileage"])
    
    # Registered owner dropdown
    await select_dropdown_option(page, "Who is the registered owner of the car?", PERSONAL_INFO["registered_owner"])
    
    # Car usage
    await select_tile_option(page, "What is the car used for?", PERSONAL_INFO["car_usage"])

    # ==================== YOUR LICENCE SECTION ====================
    print("\n--- Filling Your Licence Section ---")
    
    # Licence type
    await select_tile_option(page, "What type of licence do you have?", PERSONAL_INFO["licence_type"])
    await asyncio.sleep(0.5)
    
    # Licence duration dropdown
    await select_dropdown_option(page, "How long have you had your licence for?", PERSONAL_INFO["licence_duration"])
    
    # Penalty points
    await select_boolean_option(page, "Do you have any active penalty points?", PERSONAL_INFO["has_penalty_points"])

    # ==================== INSURANCE COVER SECTION ====================
    print("\n--- Filling Insurance Cover Section ---")
    
    # Driving experience
    await select_tile_option(page, "What is  your driving experience level?", PERSONAL_INFO["driving_experience"])
    await asyncio.sleep(0.5)

    # Fill out No Claims Discount
    await select_dropdown_option(page, "How many consecutive years have you held a private car policy in your own name without an accident or claim?", PERSONAL_INFO["no_claims_discount"])
    await asyncio.sleep(0.5)

    # Fill out Country of most recent insurance
    await select_dropdown_option(page, "In what country was your most recent no claim discount earned?", PERSONAL_INFO["country_of_most_recent_ncd"])
    await asyncio.sleep(0.5)
    
    # Fill out Previous insurer
    await select_dropdown_option(page, "Who is your current/previous insurer?", PERSONAL_INFO["previous_insurer"])
    await asyncio.sleep(0.5)
    
    # Policy start date
    await fill_date_field(page, "When do you require cover from", PERSONAL_INFO["policy_start_date"])

    # Is this the same date as current policy end date
    await select_boolean_option(page, "Is this the same as the end date of your existing policy", PERSONAL_INFO["same_as_current_policy_end_date"])
    
    # Payment type
    await select_tile_option(page, "How do you normally pay?", PERSONAL_INFO["payment_type"])

    # ==================== ADDITIONAL DRIVERS SECTION ====================
    print("\n--- Filling Additional Drivers Section ---")
    
    await select_boolean_option(page, "Would you like to add an additional driver?", PERSONAL_INFO["add_additional_driver"])

    # ==================== KEEP IN CONTACT SECTION ====================
    print("\n--- Filling Keep In Contact Section ---")
    
    await select_boolean_option(page, "From time to time we would like to contact you", PERSONAL_INFO["marketing_consent"])

    await select_boolean_option(page, "Would you like to only receive details and/or special offers in relation to our Car Insurance by Email, SMS, Post or Phone? Is this ok? (You can withdraw consent at any time.)", PERSONAL_INFO["marketing_consent"])

    # ==================== TERMS AND CONDITIONS SECTION ====================
    print("\n--- Accepting Terms and Conditions ---")
    
    if PERSONAL_INFO["accept_terms"]:
        await click_checkbox(page, "I confirm I have read and accept")

    # ==================== SUBMIT FORM ====================
    print("\n--- Form Complete ---")
    await asyncio.sleep(2)
    
    # Uncomment below to click the submit button
    await page.locator('button:has-text("Get an Indicative Price")').click()
    print("Clicked 'Get an Indicative Price' button")
    
    # Keep browser open to see results
    await asyncio.sleep(50)
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


if __name__ == "__main__":
    asyncio.run(main())
