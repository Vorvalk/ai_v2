from __future__ import annotations

from playwright.async_api import Page

from config.settings import Settings


class ParaBankMainPage:
    def __init__(self, page: Page):
        self.page = page

    @staticmethod
    def get_main_page_url() -> str:
        return Settings.get_test_url()

    async def open(self) -> None:
        await self.page.goto(self.get_main_page_url())


