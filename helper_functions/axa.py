# AXA Helper Functions

from datetime import datetime

def format_date_for_axa(date_string):
    """Convert date string to DD/MM/YYYY format for AXA"""
    if "-" in date_string:
        # Convert DD-MM-YYYY to DD/MM/YYYY
        return date_string.replace("-", "/")
    elif "/" in date_string:
        # Already in correct format
        return date_string
    else:
        # Handle other formats if needed
        return date_string

def split_date_components(date_string):
    """Split date string into day, month, year components"""
    formatted_date = format_date_for_axa(date_string)
    
    if "/" in formatted_date:
        parts = formatted_date.split("/")
        if len(parts) == 3:
            return {
                "day": parts[0],
                "month": parts[1], 
                "year": parts[2]
            }
    
    # Default fallback
    return {"day": "", "month": "", "year": ""}

def map_employment_status(occupation):
    """Map occupation to employment status for AXA"""
    occupation_lower = occupation.lower()
    
    if any(word in occupation_lower for word in ["developer", "engineer", "manager", "analyst", "consultant", "designer"]):
        return "employed"
    elif any(word in occupation_lower for word in ["self", "freelance", "contractor"]):
        return "self_employed"
    elif "student" in occupation_lower:
        return "student"
    elif "retired" in occupation_lower:
        return "retired"
    else:
        return "employed"  # Default assumption

def map_annual_distance(mileage):
    """Map estimated mileage to AXA annual distance categories"""
    if mileage <= 5000:
        return "up_to_5000"
    elif mileage <= 8000:
        return "up_to_8000"
    elif mileage <= 10000:
        return "up_to_10000"
    elif mileage <= 11000:
        return "up_to_11000"
    elif mileage <= 12000:
        return "up_to_12000"
    elif mileage <= 13000:
        return "up_to_13000"
    elif mileage <= 14000:
        return "up_to_14000"
    elif mileage <= 15000:
        return "up_to_15000"
    elif mileage <= 16000:
        return "up_to_16000"
    elif mileage <= 17000:
        return "up_to_17000"
    elif mileage <= 18000:
        return "up_to_18000"
    elif mileage <= 19000:
        return "up_to_19000"
    elif mileage <= 20000:
        return "up_to_20000"
    elif mileage <= 25000:
        return "up_to_25000"
    elif mileage <= 30000:
        return "up_to_30000"
    elif mileage <= 35000:
        return "up_to_35000"
    elif mileage <= 40000:
        return "up_to_40000"
    elif mileage <= 50000:
        return "up_to_50000"
    else:
        return "over_50000"

def map_years_licence_held(years):
    """Map years licence held to AXA categories"""
    if years < 1:
        return "less_than_1"
    elif years <= 1:
        return "1"
    elif years <= 2:
        return "2"
    elif years <= 3:
        return "3"
    elif years <= 4:
        return "4"
    elif years <= 5:
        return "5"
    elif years <= 6:
        return "6"
    elif years <= 7:
        return "7"
    elif years <= 8:
        return "8"
    elif years <= 9:
        return "9"
    else:
        return "10_plus"

def map_driving_experience(driving_experience):
    """Map driving experience to AXA categories"""
    experience_lower = driving_experience.lower()
    
    if "myself" in experience_lower or "own" in experience_lower:
        return "own_name"
    elif "named" in experience_lower:
        return "named_driver"
    elif "company" in experience_lower:
        return "company_car"
    elif "no" in experience_lower or "none" in experience_lower:
        return "no_previous"
    else:
        return "own_name"  # Default assumption

def map_licence_type(licence_type, duration):
    """Map licence type and duration to AXA licence categories"""
    licence_lower = licence_type.lower()
    
    if "full" in licence_lower:
        if duration >= 1:
            return "roi_full"  # Assume ROI if full and held for over a year
        else:
            return "roi_provisional"
    elif "provisional" in licence_lower:
        return "roi_provisional"
    elif "uk" in licence_lower:
        return "uk_full"
    elif "eu" in licence_lower:
        return "eu_full"
    else:
        return "roi_full"  # Default assumption

def format_phone_number(phone):
    """Format phone number for AXA"""
    # Remove any non-digit characters
    cleaned = ''.join(filter(str.isdigit, phone))
    return cleaned
