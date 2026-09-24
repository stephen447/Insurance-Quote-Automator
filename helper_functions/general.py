"""Helpers shared by multiple insurance providers."""

import asyncio
import random

MIN_INTERACTION_DELAY_SECONDS = 2
MAX_INTERACTION_DELAY_SECONDS = 8


async def _random_interaction_delay(min_delay, max_delay):
    """Wait for a valid randomized interaction interval."""
    if min_delay < 0 or max_delay < min_delay:
        raise ValueError("Interaction delays must satisfy 0 <= min_delay <= max_delay")
    await asyncio.sleep(random.uniform(min_delay, max_delay))


async def click_with_delay(
    locator,
    *,
    min_delay=MIN_INTERACTION_DELAY_SECONDS,
    max_delay=MAX_INTERACTION_DELAY_SECONDS,
    javascript=False,
    **click_options,
):
    """Pause for a random interval, then click a Playwright locator."""
    await _random_interaction_delay(min_delay, max_delay)
    if javascript:
        return await locator.evaluate("element => element.click()")
    return await locator.click(**click_options)


async def fill_with_delay(
    locator,
    value,
    *,
    min_delay=MIN_INTERACTION_DELAY_SECONDS,
    max_delay=MAX_INTERACTION_DELAY_SECONDS,
    **fill_options,
):
    """Pause for a random interval, then fill a text-like input."""
    await _random_interaction_delay(min_delay, max_delay)
    return await locator.fill(value, **fill_options)


async def select_option_with_delay(
    locator,
    *option_args,
    min_delay=MIN_INTERACTION_DELAY_SECONDS,
    max_delay=MAX_INTERACTION_DELAY_SECONDS,
    **option_options,
):
    """Pause for a random interval, then select a native dropdown option."""
    await _random_interaction_delay(min_delay, max_delay)
    return await locator.select_option(*option_args, **option_options)


async def set_checked_with_delay(
    locator,
    checked,
    *,
    min_delay=MIN_INTERACTION_DELAY_SECONDS,
    max_delay=MAX_INTERACTION_DELAY_SECONDS,
    **check_options,
):
    """Pause for a random interval, then set a checkbox or radio state."""
    await _random_interaction_delay(min_delay, max_delay)
    return await locator.set_checked(checked, **check_options)


async def press_with_delay(
    locator,
    key,
    *,
    min_delay=MIN_INTERACTION_DELAY_SECONDS,
    max_delay=MAX_INTERACTION_DELAY_SECONDS,
    **press_options,
):
    """Pause for a random interval, then press a key on a locator."""
    await _random_interaction_delay(min_delay, max_delay)
    return await locator.press(key, **press_options)


def capitalize_first_letter(string):
    """Capitalize the first character of a string."""
    return string.capitalize()


def format_phone(phone):
    """Remove spaces and hyphens from a phone number."""
    return phone.replace(" ", "").replace("-", "")
