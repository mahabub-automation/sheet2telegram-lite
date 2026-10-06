"""Configuration loading for Sheet2Telegram Lite.

Reads settings from environment variables. Locally these come from a .env file;
on GitHub Actions they come from repository secrets.
"""

import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Raised when a required setting is missing or malformed."""


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(
            f"Missing required setting: {name}\n"
            f"Set it in your .env file (local) or as a repository secret (GitHub Actions)."
        )
    return value


def _column_index(letter: str, name: str) -> int:
    """Convert a spreadsheet column letter (A, B, ... AA) to a 0-based index."""
    letter = letter.strip().upper()
    if not letter or not letter.isalpha():
        raise ConfigError(f"{name} must be a column letter such as A or D, got: {letter!r}")
    index = 0
    for char in letter:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


def load_credentials() -> dict:
    """Load the Google service account credentials.

    Two sources, in order of priority:
      1. GOOGLE_CREDENTIALS  - the full JSON as a string (used on GitHub Actions)
      2. credentials.json    - a file in the project root (used locally)
    """
    raw = os.getenv("GOOGLE_CREDENTIALS", "").strip()
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ConfigError(
                "GOOGLE_CREDENTIALS is set but is not valid JSON. "
                "Paste the entire contents of credentials.json, including the braces."
            ) from exc

    path = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    if not os.path.exists(path):
        raise ConfigError(
            f"No Google credentials found.\n"
            f"Either save your service account key as '{path}', "
            f"or set the GOOGLE_CREDENTIALS environment variable to its contents."
        )
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


class Config:
    """All settings for one report run."""

    def __init__(self) -> None:
        self.telegram_bot_token = _required("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = _required("TELEGRAM_CHAT_ID")

        self.sheet_id = _required("SHEET_ID")
        self.sheet_range = os.getenv("SHEET_RANGE", "Sheet1!A1:Z1000").strip()

        self.date_column = _column_index(os.getenv("DATE_COLUMN", "A"), "DATE_COLUMN")
        self.amount_column = _column_index(os.getenv("AMOUNT_COLUMN", "B"), "AMOUNT_COLUMN")

        product_column = os.getenv("PRODUCT_COLUMN", "").strip()
        self.product_column = (
            _column_index(product_column, "PRODUCT_COLUMN") if product_column else None
        )

        self.has_header = os.getenv("HAS_HEADER", "true").strip().lower() in ("1", "true", "yes")
        self.date_format = os.getenv("DATE_FORMAT", "%Y-%m-%d").strip()
        self.currency = os.getenv("CURRENCY", "$").strip()
        self.report_title = os.getenv("REPORT_TITLE", "Daily Report").strip()
        self.timezone = os.getenv("TIMEZONE", "UTC").strip()

        # Which day to report on: 1 = yesterday (default), 0 = today.
        try:
            self.days_back = int(os.getenv("DAYS_BACK", "1"))
        except ValueError:
            raise ConfigError("DAYS_BACK must be a whole number, for example 1") from None

        self.credentials = load_credentials()


def load_config() -> Config:
    """Load configuration, exiting with a readable message if anything is wrong."""
    try:
        return Config()
    except ConfigError as exc:
        print(f"[config error] {exc}", file=sys.stderr)
        sys.exit(1)
