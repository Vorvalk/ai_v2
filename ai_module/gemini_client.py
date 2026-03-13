from __future__ import annotations

import json

from google import genai
from google.genai import types

from ai_module.models import LocatorCandidatesResult, LocatorResult
from config.settings import Settings


def get_element_locator(element: str, url: str, dom: str) -> str:
    Settings.load_environment()
    api_key = Settings.get_env("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a Playwright Python locator assistant. "
                "Return only valid JSON. "
                "Do not use markdown. "
                "Do not use code fences. "
                "Do not use markdown. "
                "Do not add explanations. "
                "Return a JSON object with exactly one top-level key: "
                "\"candidates\". "
                "\"candidates\" must be a non-empty array of locator objects. "
                "Each locator object must contain exactly these keys: "
                "\"method\", \"args\", \"kwargs\". "
                "Allowed methods are: locator, get_by_text, get_by_placeholder, "
                "get_by_label, get_by_role, get_by_test_id, get_by_alt_text, get_by_title. "
                "Use the provided DOM to choose multiple locator candidates for the requested element. "
                "Order candidates from most reliable to least reliable. "
                "Prefer stable, unique selectors over brittle ones. "
                "Only use get_by_label if the DOM shows a real accessible label relationship. "
                "Only use get_by_role with a name if the accessible name is clearly supported by the DOM. "
                "If strong semantic locators are unavailable, include robust CSS locator fallbacks based on stable DOM attributes. "
                "Do not invent attributes that are not supported by the DOM."
            ),
            temperature=0.1,
        ),
        contents=(
            f"Find the best Playwright locator candidates for the element '{element}' on page '{url}'.\n\n"
            "Return 3 to 7 ordered candidates when possible.\n\n"
            f"DOM:\n{dom}"
        ),
    )

    raw_text = response.text.strip()
    data = json.loads(raw_text)

    candidates_data = data.get("candidates")
    if not isinstance(candidates_data, list) or not candidates_data:
        raise ValueError("AI response must contain a non-empty 'candidates' list.")

    result = LocatorCandidatesResult(
        candidates=[
            LocatorResult(
                method=candidate["method"],
                args=candidate.get("args", []),
                kwargs=candidate.get("kwargs", {}),
            )
            for candidate in candidates_data
        ]
    )
    result.validate()
    return result.to_json()