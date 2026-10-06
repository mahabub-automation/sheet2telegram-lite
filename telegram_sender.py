"""Send a message to a Telegram chat via the Bot API."""

from __future__ import annotations

import requests

API_BASE = "https://api.telegram.org"
TIMEOUT_SECONDS = 30


class TelegramError(Exception):
    """Raised when Telegram rejects the request."""


def send_message(bot_token: str, chat_id: str, text: str) -> None:
    """Post a message to the chat. Raises TelegramError on failure."""
    url = f"{API_BASE}/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise TelegramError(f"Could not reach Telegram: {exc}") from exc

    if response.status_code == 401:
        raise TelegramError("Telegram rejected the bot token. Check TELEGRAM_BOT_TOKEN.")

    try:
        body = response.json()
    except ValueError:
        raise TelegramError(f"Unexpected reply from Telegram (HTTP {response.status_code}).") from None

    if not body.get("ok"):
        description = body.get("description", "unknown error")
        if "chat not found" in description.lower():
            raise TelegramError(
                "Chat not found. Add the bot to the group, send one message there, "
                "then re-check TELEGRAM_CHAT_ID. Group IDs start with -100."
            )
        raise TelegramError(f"Telegram refused the message: {description}")
