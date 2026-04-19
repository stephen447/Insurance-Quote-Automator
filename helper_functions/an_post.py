from datetime import datetime
import asyncio

def format_mileage(mileage):
    # Need to be informat 0-7500, 10501-, 16501-, 18001- , 19501, 21001, 22501,.... 37501
    if mileage <= 7500:
        return "0-7500"
    elif mileage <= 10500:
        return "10501 - 16500"
    elif mileage <= 16500:
        return "16501 - 18000"
    elif mileage <= 18000:
        return "18001 - 19500"
    elif mileage <= 19500:
        return "19501 - 21000"
    elif mileage <= 21000:
        return "21001 - 22500"
    elif mileage <= 22500:
        return "22501 - 24000"
    elif mileage <= 24000:
        return "24001 - 25500"
    elif mileage <= 25500:
        return "25501 - 27000"
    elif mileage <= 27000:
        return "27001 - 28500"
    elif mileage <= 28500:
        return "28501 - 30000"
    elif mileage <= 30000:
        return "30001 - 31500"
    elif mileage <= 31500:
        return "31501 - 33000"
    elif mileage <= 33000:
        return "33001 - 34500"
    elif mileage <= 34500:
        return "34501 - 36000"
    elif mileage <= 36000:
        return "36001 - 37500"
    elif mileage <= 37500:
        return "37501 - 55000"
    else:
        return "55001 and above" 

def format_phone(phone):
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, phone))
    # Ensure it's 10 digits
    if len(phone) != 10:
        raise ValueError("Phone number must be 10 digits")
    return phone

def calculate_no_claims_discount(years):
    # Calculate the number of years between the start date and now
    if years>8:
        return "9+"
    else:
        return str(years)

async def accept_cookies(page):
    """Accept cookies if the banner appears"""
    try:
        cookie_button = page.locator('#onetrust-accept-btn-handler')

        if await cookie_button.is_visible():
            await cookie_button.click()
            print("Info: Clicked 'Accept All' for cookies")

    except Exception as e:
        print(f"Info: Cookie banner not found or already accepted: {e}")

async def click_checkbox(page, checkbox_text_contains):
    """Click a checkbox by partial label text"""
    try:
        container = page.locator(
            f'div.equote-question-base:has(span[data-cy="title"]:has-text("{checkbox_text_contains}"))'
        )

        checkbox = container.locator('p-checkbox')
        await checkbox.wait_for(state="visible")

        await checkbox.click()
        print(f"Clicked checkbox for '{checkbox_text_contains}'")

    except Exception as e:
        print(f"Error clicking checkbox for '{checkbox_text_contains}': {e}")
        raise Exception(f"Failed to click checkbox for '{checkbox_text_contains}': {e}")

async def enter_and_select_first_option_from_dropdown(page, input_selector, value):
    """Enter value and select first option from autocomplete dropdown"""
    await page.locator(input_selector).fill(value)
    await asyncio.sleep(1)
    option = page.locator('.p-autocomplete-panel .p-autocomplete-item')

    try:
        await option.first.wait_for(state="visible")

        option_count = await option.count()
        if option_count == 0:
            raise Exception(f"Option '{value}' not found in dropdown")
        if option_count > 1:
            print(f"Warning: Multiple options found for '{value}'")

        await option.first.click()
        print(f"Info: Selected first option for '{value}'")

    except Exception as e:
        print(f"Error selecting '{value}' from dropdown: {e}")
        raise Exception(f"[Dropdown] Failed to select '{value}' using selector '{input_selector}': {e}")

async def enter_and_select_from_dropdown(page, input_selector, value):
    """Enter value and select matching option from autocomplete dropdown"""
    await page.locator(input_selector).fill(value)

    option = page.locator(f'.p-autocomplete-panel .p-autocomplete-item:has-text("{value}")')

    try:
        await option.first.wait_for(state="visible")

        option_count = await option.count()
        if option_count == 0:
            raise Exception(f"Option '{value}' not found in dropdown")
        if option_count > 1:
            print(f"Warning: Multiple options found for '{value}'")

        await option.first.click()
        print(f"Info: Selected '{value}' from dropdown")

    except Exception as e:
        print(f"Error selecting '{value}' from dropdown: {e}")
        raise Exception(f"[Dropdown] Failed to select '{value}' using selector '{input_selector}': {e}")

async def fill_date_field(page, question_text, date_string):
    """Fill a date field (DD-MM-YYYY) by question text"""
    try:
        date_obj = datetime.strptime(date_string, "%d-%m-%Y")

        container = page.locator(
            f'div.equote-question-base:has(span[data-cy="title"]:has-text("{question_text}"))'
        )

        await container.locator('input[placeholder="DD"]').fill(str(date_obj.day).zfill(2))
        await container.locator('input[placeholder="MM"]').fill(str(date_obj.month).zfill(2))
        await container.locator('input[placeholder="YYYY"]').fill(str(date_obj.year))

        print(f"Filled date for '{question_text}': {date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year}")

    except Exception as e:
        print(f"Error filling date field for '{question_text}': {e}")
        raise Exception(f"Failed to fill date field for '{question_text}': {e}")

async def fill_text_field(page, question_text, value):
    """Fill a text field by question text"""
    container = page.locator(
        f'div.equote-question-base:has(span[data-cy="title"]:has-text("{question_text}"))'
    )

    field = container.locator('input')

    try:
        await field.first.wait_for(state="visible")

        field_count = await field.count()
        if field_count == 0:
            raise Exception(f"Text field not found for '{question_text}'")
        if field_count > 1:
            print(f"Info: Multiple text fields found for '{question_text}', using first one")

        await field.first.fill(value)
        print(f"Info: Filled text field for '{question_text}' with: {value}")

    except Exception as e:
        print(f"Error filling text field for '{question_text}': {e}")
        raise Exception(f"Failed to fill text field for '{question_text}': {e}")

async def select_boolean_option(page, question_text, value):
    """Select Yes/No boolean option"""
    container = page.locator(
        f'div.equote-question-base:has(span[data-cy="title"]:has-text("{question_text}"))'
    )

    checkbox = container.locator(f'div[role="button"]:has-text("{value}")')

    try:
        await checkbox.first.wait_for(state="visible")

        checkbox_count = await checkbox.count()
        if checkbox_count == 0:
            raise Exception(f"Checkbox option '{value}' not found for question '{question_text}'")
        if checkbox_count > 1:
            print(f"Warning: Multiple checkbox options found for '{value}'")

        await checkbox.first.click()
        print(f"Info: Selected '{value}' for '{question_text}'")

    except Exception as e:
        print(f"Error selecting boolean option '{value}' for '{question_text}': {e}")

async def select_dropdown_option(page, question_text, option_text):
    """Select option from PrimeNG dropdown"""
    try:
        container = page.locator(
            f'div.equote-question-base:has(span[data-cy="title"]:has-text("{question_text}"))'
        )

        await container.locator('p-dropdown').click()

        option = page.locator(f'.p-dropdown-item:has-text("{option_text}")')

        await option.first.wait_for(state="visible")
        await option.first.click()

        print(f"Selected '{option_text}' for '{question_text}'")

    except Exception as e:
        print(f"Error selecting dropdown option '{option_text}' for '{question_text}': {e}")
        raise Exception(f"Failed to select dropdown option '{option_text}' for '{question_text}': {e}")

async def select_tile_option(page, question_text, option_label):
    """Generic function to select a tile option button"""
    container = page.locator(
        f'div.equote-question-base:has(span[data-cy="title"]:has-text("{question_text}"))'
    )

    tile = container.locator(f'div[role="button"]:has-text("{option_label}")')

    try:
        await tile.first.wait_for(state="visible")

        tile_count = await tile.count()
        if tile_count == 0:
            raise Exception(f"Tile option '{option_label}' not found for question '{question_text}'")
        if tile_count > 1:
            print(f"Warning: Multiple tile options found for '{option_label}'")

        await tile.first.click()
        print(f"Info: Selected '{option_label}' for '{question_text}'")

    except Exception as e:
        print(f"Error selecting tile option '{option_label}' for '{question_text}': {e}")
        raise Exception(f"Failed to select tile option '{option_label}' for '{question_text}': {e}")