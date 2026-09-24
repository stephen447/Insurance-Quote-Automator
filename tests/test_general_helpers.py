"""Tests for helpers shared by the provider automations."""

import unittest
from unittest.mock import AsyncMock, patch

from helper_functions.general import (
    click_with_delay,
    fill_with_delay,
    press_with_delay,
    select_option_with_delay,
    set_checked_with_delay,
)


class ClickWithDelayTests(unittest.IsolatedAsyncioTestCase):
    """Verify centralized clicks pause and preserve Playwright options."""

    async def test_click_uses_random_delay_and_forwards_options(self):
        """A normal click waits for the generated interval before clicking."""
        locator = AsyncMock()

        with (
            patch("helper_functions.general.random.uniform", return_value=0.42),
            patch(
                "helper_functions.general.asyncio.sleep", new_callable=AsyncMock
            ) as sleep,
        ):
            await click_with_delay(locator, min_delay=0.2, max_delay=0.8, timeout=3000)

        sleep.assert_awaited_once_with(0.42)
        locator.click.assert_awaited_once_with(timeout=3000)

    async def test_javascript_click_uses_same_delay(self):
        """JavaScript-backed controls still use the centralized pause."""
        locator = AsyncMock()

        with (
            patch("helper_functions.general.random.uniform", return_value=0.3),
            patch(
                "helper_functions.general.asyncio.sleep", new_callable=AsyncMock
            ) as sleep,
        ):
            await click_with_delay(locator, javascript=True)

        sleep.assert_awaited_once_with(0.3)
        locator.evaluate.assert_awaited_once_with("element => element.click()")
        locator.click.assert_not_awaited()

    async def test_text_input_uses_delay_and_forwards_options(self):
        """Text-like fields use the shared delay before being filled."""
        locator = AsyncMock()

        with (
            patch("helper_functions.general.random.uniform", return_value=0.5),
            patch(
                "helper_functions.general.asyncio.sleep", new_callable=AsyncMock
            ) as sleep,
        ):
            await fill_with_delay(locator, "value", force=True)

        sleep.assert_awaited_once_with(0.5)
        locator.fill.assert_awaited_once_with("value", force=True)

    async def test_dropdown_checkbox_and_key_press_use_delay(self):
        """Other input types all route through the shared randomized pause."""
        dropdown = AsyncMock()
        checkbox = AsyncMock()
        keyboard_input = AsyncMock()

        with (
            patch("helper_functions.general.random.uniform", return_value=0.4),
            patch(
                "helper_functions.general.asyncio.sleep", new_callable=AsyncMock
            ) as sleep,
        ):
            await select_option_with_delay(dropdown, value="option-1")
            await set_checked_with_delay(checkbox, True, force=True)
            await press_with_delay(keyboard_input, "Enter", timeout=2000)

        self.assertEqual(sleep.await_count, 3)
        dropdown.select_option.assert_awaited_once_with(value="option-1")
        checkbox.set_checked.assert_awaited_once_with(True, force=True)
        keyboard_input.press.assert_awaited_once_with("Enter", timeout=2000)

    async def test_invalid_delay_range_is_rejected(self):
        """Invalid delay settings fail before interacting with the page."""
        locator = AsyncMock()

        with self.assertRaises(ValueError):
            await click_with_delay(locator, min_delay=1, max_delay=0.5)

        locator.click.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
