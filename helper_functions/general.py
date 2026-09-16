"""Helpers shared by multiple insurance providers."""


def capitalize_first_letter(string):
    return string.capitalize()


def format_phone(phone):
    return phone.replace(" ", "").replace("-", "")
