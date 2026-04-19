import asyncio
from playwright.async_api import Playwright, async_playwright
from data_maps.an_post import AN_POST_MAPPINGS
from helper_functions.an_post import format_mileage, calculate_no_claims_discount, accept_cookies, enter_and_select_from_dropdown, select_tile_option, select_boolean_option, fill_date_field, fill_text_field, enter_and_select_first_option_from_dropdown, select_dropdown_option, click_checkbox
import helper_functions.general as general_helpers
from datetime import datetime

async def run(playwright: Playwright, data):
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto("https://insurance.anpostinsurance.ie/v2/equote/motor/risk")
    
    # Accept cookies
    await accept_cookies(page)
    await asyncio.sleep(1)

    # ==================== YOUR DETAILS SECTION ====================
    print("\n--- Filling Your Details Section ---")
    
    await select_tile_option(page, "Title", AN_POST_MAPPINGS["title"][data["title"]])
    await fill_text_field(page, "First Name", data["first_name"])
    await fill_text_field(page, "Last Name", data["last_name"])
    await fill_date_field(page, "Date of Birth", data["date_of_birth"])
    await fill_text_field(page, "Mobile Number", general_helpers.format_phone(data["phone"]))
    await fill_text_field(page, "Email", data["email"])
    await enter_and_select_from_dropdown(page, "[placeholder='Begin typing...']", data["occupation"])

    # ==================== YOUR CAR SECTION ====================
    print("\n--- Filling Your Car Section ---")
    
    await enter_and_select_first_option_from_dropdown(page, "[placeholder='Start typing your Eircode or address']", data["address"]["postal_code"])
    
    await fill_text_field(page, "What is the registration number of the car?", data["car_registration"])
    # Click the registration button
    await page.locator('button:has-text("Find your Vehicle")').click()
    await asyncio.sleep(2)
    
    await fill_text_field(page, "What is the current market value of the car?", str(data["car_value"]))
    
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
    await select_tile_option(page, "What is your driving experience level?", AN_POST_MAPPINGS["driving_experience"][data["driving_experience"]])
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
    await asyncio.sleep(1)

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
    await asyncio.sleep(1)
    
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


