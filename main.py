import asyncio
from datetime import datetime

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

import companies.an_post as an_post
import companies.axa as axa


PROVIDERS = (
    ("An Post Insurance", an_post.run),
    ("AXA Insurance", axa.run),
)

# Personal information dictionary
PERSONAL_INFO = {
    "title": "mr",
    "first_name": "stephen",
    "last_name": "byrne",
    "email": "stephen.byrne@example.com",
    "phone": "083-8128391",
    "date_of_birth": "11-01-1999",
    "occupation": "software developer",
    "car_registration": "12-D-12345",
    "car_value": 15000,
    "car_purchase_date": "15-06-2023",
    "estimated_mileage": 10000,
    "right_hand_drive": True,
    "registered_in_ireland": True,
    "is_imported": False,
    "registered_owner": "proposer",
    "car_usage": "social",
    "address": {
        "street": "123 main street",
        "city": "malahide",
        "county": "dublin",
        "country": "ireland",
        "postal_code": "k36cf34"
    },
    # Licence section
    "licence_type": "full",
    "licence_duration": 5,
    "has_penalty_points": False,
    # Insurance Cover section
    "driving_experience": "myself",
    "no_claims_discount": 4,
    "country_of_most_recent_ncd": "ireland",
    "previous_insurer": "allianz",
    "policy_start_date": "01-10-2026",
    "same_as_current_policy_end_date": True,
    "payment_type": "full",
    # Additional Drivers
    "add_additional_driver": False,
    # Marketing
    "marketing_consent": False,
    # Terms
    "accept_terms": True
}


def initialise_report():
    """Create a fresh report for the current comparison run."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("insurance_quotes.txt", "w") as f:
        f.write("Insurance Quote Comparison Report\n")
        f.write(f"Generated: {timestamp}\n")
        f.write(f"Personal Details: {PERSONAL_INFO['first_name']} {PERSONAL_INFO['last_name']}\n")
        f.write(f"Vehicle: {PERSONAL_INFO['car_registration']}\n")
        f.write(f"{'='*50}\n\n")


def record_provider_failure(provider_name, error):
    """Record a failed provider without stopping the comparison run."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("insurance_quotes.txt", "a") as f:
        f.write(f"Company: {provider_name}\n")
        f.write(f"Quote Attempted: {timestamp}\n")
        f.write("Status: Failed\n")
        f.write(f"Error: {error}\n")
        f.write(f"{'='*50}\n\n")


async def run_all_providers():
    """Run each insurance provider sequentially with stealth enabled."""
    async with Stealth().use_async(async_playwright()) as playwright:
        for provider_name, run_provider in PROVIDERS:
            print(f"\n{'='*50}")
            print(f"Running quote for {provider_name}")
            print(f"{'='*50}")

            try:
                await run_provider(playwright, PERSONAL_INFO)
            except Exception as error:
                print(f"{provider_name} failed: {error}")
                record_provider_failure(provider_name, error)


def main():
    initialise_report()
    asyncio.run(run_all_providers())


if __name__ == "__main__":
    main()
