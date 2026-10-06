# Sheet2Telegram Lite

Send a daily summary of your Google Sheet to a Telegram chat — automatically, for free, forever.

No Zapier. No Make. No monthly subscription. Runs on GitHub Actions' free tier.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Runs on](https://img.shields.io/badge/runs%20on-GitHub%20Actions-black.svg)

---

## The problem

Every morning, the same ritual: open the sheet, scan yesterday's rows, add it up, type the summary into the group chat.

Five minutes a day. Twenty-five hours a year.

Zapier and Make will do this for you — for $20–30/month, forever. This repo does it for $0.

## What you get

```
📊 Daily Sales Report
05 Oct 2026

Total:    BDT 48,250
Entries:  37
Average:  BDT 1,304.05
Top item: Premium Tea Pack (12)
```

Delivered to your Telegram group every morning, with nothing running on your computer.

---

## How it works

```
Google Sheet  →  GitHub Actions (free)  →  Telegram group
```

Three moving parts. A sheet you already keep. A Python script that reads yesterday's rows and totals them. GitHub Actions, which runs that script on a schedule so you don't need a server.

---

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/mahabub-automation/sheet2telegram-lite.git
cd sheet2telegram-lite
pip install -r requirements.txt
```

### 2. Create a Telegram bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the token it gives you
4. Add the bot to your group, then send any message in that group
5. Get your chat ID:

```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

Look for `"chat":{"id":-1001234567890` — that number is your chat ID. Group IDs start with `-100`.

### 3. Connect Google Sheets

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project
2. Enable the **Google Sheets API**
3. Create a **Service Account**, then create a JSON key and download it
4. Save that file as `credentials.json` in the project root
5. Open the JSON and copy the `client_email` value (it ends in `.iam.gserviceaccount.com`)
6. Open your Google Sheet → **Share** → paste that email → give it **Viewer** access

Step 6 is where most people get stuck. The service account is treated like a person — if you don't share the sheet with it, it can't read anything.

### 4. Configure

```bash
cp .env.example .env
```

Then edit `.env`:

| Setting | What it is |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From BotFather |
| `TELEGRAM_CHAT_ID` | Your group or chat ID |
| `SHEET_ID` | The long id in your sheet URL: `docs.google.com/spreadsheets/d/`**`SHEET_ID`**`/edit` |
| `SHEET_RANGE` | Tab and cells to read, e.g. `Sheet1!A1:F1000` |
| `DATE_COLUMN` | Column letter holding the date, e.g. `A` |
| `AMOUNT_COLUMN` | Column letter holding the number to total, e.g. `D` |
| `PRODUCT_COLUMN` | Optional. Adds a "Top item" line. Leave blank to skip. |
| `HAS_HEADER` | `true` if row 1 is headers |
| `DATE_FORMAT` | How dates are written in your sheet, e.g. `%Y-%m-%d` |
| `CURRENCY` | Symbol shown in the report, e.g. `$` or `BDT` |
| `TIMEZONE` | IANA zone used to work out "yesterday", e.g. `Asia/Dhaka` |
| `DAYS_BACK` | `1` for yesterday, `0` for today |

### 5. Test it

Preview the report without sending anything:

```bash
python main.py --dry-run
```

Got the numbers you expected? Send it for real:

```bash
python main.py
```

---

## Scheduling it (the free part)

You don't need a server. GitHub Actions runs this on a schedule for free.

**1.** Push your own copy of this repo to GitHub. **Make it private** — it will hold your secrets.

**2.** Go to **Settings → Secrets and variables → Actions** and add these four secrets:

| Secret | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | your bot token |
| `TELEGRAM_CHAT_ID` | your chat ID |
| `SHEET_ID` | your sheet ID |
| `GOOGLE_CREDENTIALS` | the entire contents of `credentials.json`, braces included |

Everything else (columns, currency, timezone) goes in the **Variables** tab on that same page, using the same names as in `.env`. Anything you skip falls back to a sensible default.

**3.** The workflow in `.github/workflows/daily-report.yml` is already set up:

```yaml
on:
  schedule:
    - cron: '30 3 * * *'   # 03:30 UTC = 09:30 Asia/Dhaka
  workflow_dispatch:        # lets you run it manually too
```

Cron always runs in **UTC** — subtract your offset to get the time you want.

**4.** Open the **Actions** tab and trigger it once manually to confirm it works.

That's it. It runs every morning now, on nobody's server, for nothing.

---

## Project structure

```
sheet2telegram-lite/
├── main.py                 # entry point, --dry-run flag
├── config.py               # loads and validates settings
├── data_reader.py          # reads the sheet, filters to one day
├── report_builder.py       # formats the message
├── telegram_sender.py      # sends to Telegram
├── requirements.txt
├── .env.example
└── .github/workflows/
    └── daily-report.yml
```

---

## Troubleshooting

**"The caller does not have permission"** — You didn't share the sheet with the service account email. See step 3.6.

**"Chat not found"** — The bot isn't in the group, or the chat ID is wrong. Add the bot, send one message in the group, then check `getUpdates` again.

**"Unable to parse range"** — `SHEET_RANGE` has the wrong tab name. Use it exactly as it appears on the tab, including spaces.

**Report says "No entries recorded"** — Run `python main.py --dry-run` and check the printed report date. Usually `DATE_FORMAT` doesn't match how dates are written in your sheet, or `DAYS_BACK` is pointing at the wrong day.

**Workflow runs but nothing arrives** — Check the Actions log. Nine times out of ten a secret is missing, or `GOOGLE_CREDENTIALS` was pasted without the outer braces.

---

## Lite vs Pro

Lite handles one sheet, one group, one fixed report format. That covers most people.

| | Lite (this repo) | Pro |
|---|---|---|
| Google Sheets → Telegram | ✅ | ✅ |
| Scheduled daily run | ✅ | ✅ |
| Dry-run preview | ✅ | ✅ |
| Multiple sheets / tabs | — | ✅ |
| Multiple Telegram groups | — | ✅ |
| Custom report templates | — | ✅ |
| Day-over-day comparison | — | ✅ |
| Charts attached as images | — | ✅ |
| WhatsApp delivery | — | ✅ |
| Setup support | — | ✅ |

**One payment. No subscription. Yours forever.**

👉 **[Get Sheet2Telegram Pro — $29](https://konyhaze.gumroad.com/l/ijikux)**

Against Zapier at $20/month, it pays for itself in six weeks.

---

## License

MIT — use it, modify it, ship it commercially. Attribution appreciated, not required.

---

Built by [Mahabubul Hasan](https://github.com/mahabub-automation) — I build automation tools that replace monthly subscriptions with one-time scripts.

If this saved you a subscription, a ⭐ helps other people find it.
