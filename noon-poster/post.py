import json
import os
import sys
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

CONTENT_FILE = "content.json"
STATE_FILE = "post_state.json"


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    content = load_json(CONTENT_FILE, [])
    if not content:
        print("content.json ထဲမှာ content မရှိပါ")
        sys.exit(1)

    state = load_json(STATE_FILE, {"last_index": 0})
    idx = state["last_index"]

    if idx >= len(content):
        print(f"Content အားလုံး ({len(content)} ရက်) တင်ပြီးသွားပါပြီ။ content.json ကို ထပ်ဖြည့်ပါ။")
        sys.exit(0)

    post = content[idx]
    text = post["text"]

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
        },
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"Telegram post မအောင်မြင်ပါ: {resp.status_code} {resp.text}")
        sys.exit(1)

    print(f"Day {post.get('day', idx + 1)} ကို post တင်ပြီးပါပြီ။")

    state["last_index"] = idx + 1
    save_json(STATE_FILE, state)


if __name__ == "__main__":
    main()
