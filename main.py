"""Run insurance quote automation for the selected providers."""

import asyncio
from datetime import datetime

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

import companies.allianz as allianz
import companies.an_post as an_post
import companies.axa as axa

PROVIDERS = {
    "an-post": ("An Post Insurance", an_post.run),
    "allianz": ("Allianz Insurance", allianz.run),
    "axa": ("AXA Insurance", axa.run),
}

# Select the companies to run here.
# Examples:
#   ("an-post",)        - An Post only
#   ("allianz",)        - Allianz only (automation in progress)
#   ("axa",)            - AXA only
#   ("an-post", "axa") - multiple companies
SELECTED_PROVIDERS = ("axa",)

# Personal information dictionary
PERSONAL_INFO = {
    "title": "mr",
    "first_name": "stephen",
    "last_name": "byrne",
    "email": "stephen.byrne@example.com",
    "phone": "083-8128391",
    "date_of_birth": "11-01-1999",
    "gender": "male",
    "employment_status": "employed",
    "occupation": "software developer",
    "car_registration": "12-D-12345",
    "car_value": 15000,
    "car_purchase_date": "15-06-2023",
    "estimated_mileage": 10000,
    "business_use": False,
    "commuting": False,
    "business_mileage": 0,
    "soliciting_orders": False,
    "regular_use_other_vehicle": False,
    "other_vehicle_types": [],
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
        "postal_code": "k36cf34",
    },
    # Licence section
    "licence_type": "full",
    "licence_duration": 5,
    "has_penalty_points": False,
    "penalty_points": 0,
    "driving_test_passed_in_ireland_uk": True,
    "driving_test_year": 2020,
    # Insurance Cover section
    "driving_experience": "myself",
    "latest_driving_experience": "policy_own_name_ireland",
    "driving_experience_years": 5,
    "no_claims_discount": 4,
    "has_claims": False,
    "country_of_most_recent_ncd": "ireland",
    "previous_insurer": "allianz",
    "policy_start_date": "01-10-2026",
    "car_parked_at_home": True,
    "existing_allianz_policy": False,
    "same_as_current_policy_end_date": True,
    "payment_type": "full",
    # Additional Drivers
    "add_additional_driver": False,
    # Marketing
    "marketing_consent": False,
    # Terms
    "accept_terms": True,
}


def initialise_report():
    """Create a fresh report for the current comparison run."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("insurance_quotes.txt", "w", encoding="utf-8") as f:
        f.write("Insurance Quote Comparison Report\n")
        f.write(f"Generated: {timestamp}\n")
        f.write(
            f"Personal Details: {PERSONAL_INFO['first_name']} {PERSONAL_INFO['last_name']}\n"
        )
        f.write(f"Vehicle: {PERSONAL_INFO['car_registration']}\n")
        f.write(f"{'='*50}\n\n")


def record_provider_failure(provider_name, error):
    """Record a failed provider without stopping the comparison run."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("insurance_quotes.txt", "a", encoding="utf-8") as f:
        f.write(f"Company: {provider_name}\n")
        f.write(f"Quote Attempted: {timestamp}\n")
        f.write("Status: Failed\n")
        f.write(f"Error: {error}\n")
        f.write(f"{'='*50}\n\n")


async def run_selected_providers():
    """Run the providers selected in SELECTED_PROVIDERS."""
    unknown_providers = set(SELECTED_PROVIDERS) - set(PROVIDERS)
    if unknown_providers:
        available = ", ".join(PROVIDERS)
        unknown = ", ".join(sorted(unknown_providers))
        raise ValueError(
            f"Unknown provider(s): {unknown}. Available providers: {available}"
        )

    async with Stealth().use_async(async_playwright()) as playwright:
        for provider_key in SELECTED_PROVIDERS:
            provider_name, run_provider = PROVIDERS[provider_key]
            print(f"\n{'='*50}")
            print(f"Running quote for {provider_name}")
            print(f"{'='*50}")

            try:
                await run_provider(playwright, PERSONAL_INFO)
            except Exception as error:
                print(f"{provider_name} failed: {error}")
                record_provider_failure(provider_name, error)


def main():
    """Initialize the report and run the configured providers."""
    initialise_report()
    asyncio.run(run_selected_providers())


if __name__ == "__main__":
    main()
