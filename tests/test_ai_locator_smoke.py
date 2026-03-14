import asyncio
import json

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from ai_module.service import get_element_locator
from pages.parabank_main_page import ParaBankMainPage


def build_locator_from_data(page, data: dict):
    method = data["method"]
    args = data.get("args", [])
    kwargs = data.get("kwargs", {})

    playwright_method = getattr(page, method, None)
    if playwright_method is None:
        raise ValueError(f"Page has no method named '{method}'")

    return playwright_method(*args, **kwargs)


def parse_locator_candidates(locator_json: str) -> list[dict]:
    data = json.loads(locator_json)

    if "candidates" in data:
        candidates = data["candidates"]
        if not isinstance(candidates, list) or not candidates:
            raise ValueError("'candidates' must be a non-empty list")

        normalized = []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                raise ValueError("Each candidate must be an object")
            if "method" not in candidate:
                raise ValueError("Each candidate must include 'method'")
            normalized.append(
                {
                    "method": candidate["method"],
                    "args": candidate.get("args", []),
                    "kwargs": candidate.get("kwargs", {}),
                }
            )
        return normalized

    if "method" in data:
        return [
            {
                "method": data["method"],
                "args": data.get("args", []),
                "kwargs": data.get("kwargs", {}),
            }
        ]

    raise ValueError("Locator JSON must contain either a single locator or 'candidates'")


async def is_good_text_input(locator) -> bool:
    try:
        first = locator.first

        if await first.count() == 0:
            return False

        await first.wait_for(state="visible", timeout=2000)

        if not await first.is_visible():
            return False

        tag_name = await first.evaluate("(el) => el.tagName.toLowerCase()")
        if tag_name not in {"input", "textarea"}:
            return False

        is_disabled = await first.evaluate("(el) => el.disabled === true")
        if is_disabled:
            return False

        input_type = await first.evaluate(
            "(el) => el.getAttribute('type') ? el.getAttribute('type').toLowerCase() : ''"
        )
        if tag_name == "input" and input_type not in {"", "text", "email", "search"}:
            return False

        return True
    except PlaywrightTimeoutError:
        return False
    except Exception:
        return False


async def resolve_locator(page, locator_json: str):
    candidates = parse_locator_candidates(locator_json)
    errors = []

    for index, candidate in enumerate(candidates, start=1):
        print(f"Trying AI candidate #{index}: {candidate}")
        try:
            locator = build_locator_from_data(page, candidate)
            if await is_good_text_input(locator):
                print(f"Resolved element using candidate #{index}: {candidate}")
                return locator.first
            errors.append(f"Candidate #{index} did not match a visible text input: {candidate}")
        except Exception as exc:
            errors.append(f"Candidate #{index} failed: {candidate} -> {exc}")

    joined = "\n".join(errors)
    raise RuntimeError(f"No valid locator candidate resolved the username field.\n{joined}")


async def run_test() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            main_page = ParaBankMainPage(page)
            await main_page.open()

            dom = await page.content()

            locator_json = get_element_locator(
                "username text input field",
                main_page.get_main_page_url(),
                dom,
            )

            print(f"AI locator response: {locator_json}")

            username_field = await resolve_locator(page, locator_json)

            assert await username_field.is_visible()
            await username_field.fill("guest")
            assert await username_field.input_value() == "guest"
            await page.pause()
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())