"""
Crypto News Auto-Poster
------------------------
Fetches latest crypto news from CryptoPanic API + RSS feeds (CoinDesk, CoinTelegraph),
filters out articles already posted before, then sends up to MAX_ITEMS new articles
to a Telegram channel in one message. Keeps a history file (posted_history.json) so
the same article never gets posted twice.

Required environment variables (set as GitHub Secrets):
  TELEGRAM_BOT_TOKEN   - Telegram bot token from @BotFather
  TELEGRAM_CHAT_ID     - Target channel ID (e.g. @yourchannel or -100xxxxxxxxxx)
  CRYPTOPANIC_TOKEN    - (optional) free token from cryptopanic.com/developers/api
"""

import os
import json
import time
import requests
import feedparser
from datetime import datetime, timezone
from dateutil import parser as dateparser
from deep_translator import GoogleTranslator

# ---------- Config ----------
HISTORY_FILE = "crypto-news-poster/posted_history.json"
MAX_ITEMS = 5          # max number of news items per post
MAX_HISTORY = 500      # cap history file size

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CRYPTOPANIC_TOKEN = os.environ.get("CRYPTOPANIC_TOKEN", "")

RSS_FEEDS = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
]

TIME_LABELS = {
    0: "🌅 မနက်ခင်း",
    5: "☀️ နေ့လယ်",
    12: "🌙 ညနေ",
}


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_history(history_set):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    trimmed = list(history_set)[-MAX_HISTORY:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)


def fetch_cryptopanic():
    if not CRYPTOPANIC_TOKEN:
        return []
    url = "https://cryptopanic.com/api/v1/posts/"
    params = {"auth_token": CRYPTOPANIC_TOKEN, "public": "true", "kind": "news"}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        items = []
        for post in data.get("results", []):
            items.append({
                "title": post.get("title", "").strip(),
                "link": post.get("url", ""),
                "source": post.get("source", {}).get("title", "CryptoPanic"),
                "published": post.get("published_at", ""),
            })
        return items
    except Exception as e:
        print(f"[CryptoPanic] fetch error: {e}")
        return []


def fetch_rss():
    items = []
    for name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                items.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "source": name,
                    "published": entry.get("published", ""),
                })
        except Exception as e:
            print(f"[RSS:{name}] fetch error: {e}")
    return items


def parse_date_safe(value):
    try:
        dt = dateparser.parse(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def translate_to_burmese(text):
    if not text:
        return text
    try:
        result = GoogleTranslator(source="auto", target="my").translate(text)
        time.sleep(0.5)  # be gentle with the free translation endpoint
        return result
    except Exception as e:
        print(f"[Translate] failed, using original text: {e}")
        return text


def escape_html(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def build_message(items, time_label):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"📰 <b>Crypto သတင်းများ</b> — {time_label} ({now})\n"]
    for i, item in enumerate(items, 1):
        title_my = escape_html(translate_to_burmese(item["title"]))
        lines.append(f'{i}. <a href="{item["link"]}">{title_my}</a>\n   <i>အရင်းအမြစ်: {item["source"]}</i>')
    return "\n".join(lines)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    r = requests.post(url, data=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def main():
    if not BOT_TOKEN or not CHAT_ID:
        raise SystemExit("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing.")

    history = load_history()
    all_items = fetch_cryptopanic() + fetch_rss()

    # sort newest-first across all sources combined
    all_items.sort(key=lambda x: parse_date_safe(x.get("published", "")), reverse=True)

    # dedupe by link, keep only unseen items, preserve order
    seen_in_batch = set()
    new_items = []
    for item in all_items:
        link = item["link"]
        if not link or link in history or link in seen_in_batch:
            continue
        seen_in_batch.add(link)
        new_items.append(item)

    if not new_items:
        print("No new crypto news found this run.")
        return

    new_items = new_items[:MAX_ITEMS]

    hour = datetime.now(timezone.utc).hour
    label = TIME_LABELS.get(hour, "🕐 Update")

    message = build_message(new_items, label)
    send_telegram(message)
    print(f"Posted {len(new_items)} new articles.")

    for item in new_items:
        history.add(item["link"])
    save_history(history)


if __name__ == "__main__":
    main()
