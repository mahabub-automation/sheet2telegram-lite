"""Turn a day's rows into the message that gets sent to Telegram."""

from __future__ import annotations

from collections import Counter
from datetime import date

from data_reader import Row


def _money(amount: float, currency: str) -> str:
    return f"{currency} {amount:,.2f}".replace(".00", "")


def _escape(text: str) -> str:
    """Escape the characters Telegram's HTML parse mode cares about."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_report(day: date, rows: list[Row], currency: str, title: str) -> str:
    """Build the Telegram message body (HTML parse mode)."""
    heading = f"<b>📊 {_escape(title)}</b>\n<i>{day.strftime('%d %b %Y')}</i>"

    if not rows:
        return f"{heading}\n\nNo entries recorded for this date."

    total = sum(row.amount for row in rows)
    count = len(rows)
    average = total / count

    lines = [
        heading,
        "",
        f"<b>Total:</b>   {_money(total, currency)}",
        f"<b>Entries:</b> {count}",
        f"<b>Average:</b> {_money(average, currency)}",
    ]

    products = [row.product for row in rows if row.product]
    if products:
        name, hits = Counter(products).most_common(1)[0]
        lines.append(f"<b>Top item:</b> {_escape(name)} ({hits})")

    return "\n".join(lines)
