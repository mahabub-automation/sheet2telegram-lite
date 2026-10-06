"""Read rows from a Google Sheet and filter them down to a single day."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Date formats tried in order when DATE_FORMAT does not match a cell.
FALLBACK_DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%d %b %Y",
    "%d %B %Y",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
]


@dataclass
class Row:
    """One matching row from the sheet."""

    amount: float
    product: str | None


def target_date(days_back: int, tz_name: str) -> date:
    """The calendar date the report covers, in the configured timezone."""
    try:
        now = datetime.now(ZoneInfo(tz_name))
    except Exception:
        now = datetime.now(timezone.utc)
    return (now - timedelta(days=days_back)).date()


def parse_date(value: str, preferred_format: str) -> date | None:
    """Parse a cell into a date, trying the configured format first."""
    value = value.strip()
    if not value:
        return None

    for fmt in [preferred_format, *FALLBACK_DATE_FORMATS]:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(value: str) -> float | None:
    """Parse a cell into a number, tolerating currency symbols and thousands separators."""
    value = value.strip()
    if not value:
        return None

    cleaned = re.sub(r"[^\d.\-]", "", value.replace(",", ""))
    if cleaned in ("", "-", ".", "-."):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def fetch_rows(config) -> list[list[str]]:
    """Pull the raw cell values from the sheet."""
    credentials = Credentials.from_service_account_info(config.credentials, scopes=SCOPES)
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

    response = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=config.sheet_id, range=config.sheet_range)
        .execute()
    )
    return response.get("values", [])


def read_day(config) -> tuple[date, list[Row]]:
    """Return the report date and every row belonging to it."""
    raw_rows = fetch_rows(config)
    if config.has_header and raw_rows:
        raw_rows = raw_rows[1:]

    day = target_date(config.days_back, config.timezone)
    matched: list[Row] = []

    for raw in raw_rows:
        if len(raw) <= max(config.date_column, config.amount_column):
            continue

        row_date = parse_date(raw[config.date_column], config.date_format)
        if row_date != day:
            continue

        amount = parse_amount(raw[config.amount_column])
        if amount is None:
            continue

        product = None
        if config.product_column is not None and len(raw) > config.product_column:
            product = raw[config.product_column].strip() or None

        matched.append(Row(amount=amount, product=product))

    return day, matched
