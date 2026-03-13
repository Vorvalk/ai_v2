from __future__ import annotations

from ai_module.gemini_client import get_element_locator as get_gemini_locator
from config.settings import Settings


PROVIDERS = {
    "gemini": get_gemini_locator,
}


def get_element_locator(element: str, url: str, dom: str) -> str:
    provider = Settings.get_active_provider()

    if provider not in PROVIDERS:
        supported = ", ".join(sorted(PROVIDERS))
        raise ValueError(
            f"Unsupported AI provider '{provider}'. Supported providers: {supported}"
        )

    return PROVIDERS[provider](element, url, dom)