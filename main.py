import asyncio
from playwright.async_api import Playwright, async_playwright, expect
import companies.an_post as an_post

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
    "policy_start_date": "01-05-2026",
    "same_as_current_policy_end_date": True,
    "payment_type": "full",
    # Additional Drivers
    "add_additional_driver": False,
    # Marketing
    "marketing_consent": False,
    # Terms
    "accept_terms": True
}


if __name__ == "__main__":
    # Create insurance quotes file with header
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open("insurance_quotes.txt", "w") as f:
        f.write(f"Insurance Quote Comparison Report\n")
        f.write(f"Generated: {timestamp}\n")
        f.write(f"Personal Details: {PERSONAL_INFO['first_name']} {PERSONAL_INFO['last_name']}\n")
        f.write(f"Vehicle: {PERSONAL_INFO['car_registration']}\n")
        f.write(f"{'='*50}\n\n")
    
    # Run An Post quote
    asyncio.run(an_post.main(PERSONAL_INFO))
