from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "config.json"
ENV_FILE = BASE_DIR / ".env"


class Settings:
    @staticmethod
    def load_environment() -> None:
        load_dotenv(dotenv_path=ENV_FILE)

    @staticmethod
    def load_config() -> dict:
        if not CONFIG_FILE.exists():
            raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")

        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("config.json must contain a JSON object.")

        return data

    @classmethod
    def get_active_provider(cls) -> str:
        config = cls.load_config()
        provider = config.get("active_ai_provider")

        if not isinstance(provider, str) or not provider.strip():
            raise ValueError("config.json must define 'active_ai_provider'.")

        return provider.strip().lower()

    @classmethod
    def get_test_url(cls) -> str:
        config = cls.load_config()
        url = config.get("test_environment", {}).get("url")

        if not isinstance(url, str) or not url.strip():
            raise ValueError("config.json must define test_environment.url.")

        return url.strip()

    @staticmethod
    def get_env(name: str) -> str:
        value = os.getenv(name)
        if not value or not value.strip():
            raise ValueError(f"Missing required environment variable: {name}")
        return value.strip()