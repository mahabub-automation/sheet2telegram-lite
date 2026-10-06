"""Sheet2Telegram Lite — send a daily Google Sheets summary to Telegram.

Run it manually:
    python main.py

Preview without sending:
    python main.py --dry-run
"""

from __future__ import annotations

import argparse
import sys

from config import load_config
from data_reader import read_day
from report_builder import build_report
from telegram_sender import TelegramError, send_message


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a daily Google Sheets summary to Telegram.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the report instead of sending it. Useful for testing your column settings.",
    )
    args = parser.parse_args()

    config = load_config()

    print("Reading sheet...")
    try:
        day, rows = read_day(config)
    except Exception as exc:  # noqa: BLE001 - surface the real cause to the user
        message = str(exc)
        if "caller does not have permission" in message or "PERMISSION_DENIED" in message:
            print(
                "[error] The service account cannot open this sheet.\n"
                "        Share the sheet with the client_email from your credentials file "
                "(it ends in .iam.gserviceaccount.com) and give it Viewer access.",
                file=sys.stderr,
            )
            return 1
        if "Unable to parse range" in message:
            print(
                f"[error] SHEET_RANGE is not valid: {config.sheet_range}\n"
                "        Use the tab name exactly as it appears, for example: Sheet1!A1:F1000",
                file=sys.stderr,
            )
            return 1
        print(f"[error] Could not read the sheet: {message}", file=sys.stderr)
        return 1

    print(f"Report date: {day}  |  matching rows: {len(rows)}")

    report = build_report(day, rows, config.currency, config.report_title)

    if args.dry_run:
        print("\n--- dry run, nothing sent ---\n")
        print(report)
        return 0

    print("Sending to Telegram...")
    try:
        send_message(config.telegram_bot_token, config.telegram_chat_id, report)
    except TelegramError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    print("Sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
