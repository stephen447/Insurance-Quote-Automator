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