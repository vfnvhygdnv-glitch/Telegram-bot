import json
import os
import sys
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
OWNER_ID = "5911159063"  # Thiha Tun's Telegram ID

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


def send_message(chat_id, text, parse_mode=None):
    """Send a message to a chat."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    resp = requests.post(url, json=payload, timeout=30)
    return resp


def main():
    content = load_json(CONTENT_FILE, [])
    if not content:
        print("content.json ထဲမှာ content မရှိပါ")
        sys.exit(1)

    state = load_json(STATE_FILE, {"last_index": 0})
    idx = state["last_index"]

    # Loop back to day 1 when all days are done
    if idx >= len(content):
        idx = 0
        print(f"Content အားလုံး တင်ပြီးသွားပါပြီ။ Day 1 ကနေ ပြန်စပါမယ်။")

    post = content[idx]
    text = post["text"]

    # Add @ThihaDigitalBot link if not present
    if "@ThihaDigitalBot" not in text:
        text += "\n\n🤖 ဝယ်ယူရန်: @ThihaDigitalBot"

    # Send to channel
    resp = send_message(CHAT_ID, text, parse_mode="HTML")

    if resp.status_code != 200:
        print(f"Telegram post မအောင်မြင်ပါ: {resp.status_code} {resp.text}")
        # Notify owner about failure
        send_message(OWNER_ID, f"❌ Channel Auto-Post (Day {idx + 1}/{len(content)}) fail ဖြစ်ပါတယ်: {resp.text}")
        sys.exit(1)

    day_num = post.get('day', idx + 1)
    print(f"Day {day_num} ကို post တင်ပြီးပါပြီ။")

    # Notify owner about successful post
    send_message(OWNER_ID, f"📢 Channel Auto-Post (Day {idx + 1}/{len(content)}) တင်ပြီးပါပြီ ✅")

    # Move to next day
    state["last_index"] = idx + 1
    save_json(STATE_FILE, state)


if __name__ == "__main__":
    main()
