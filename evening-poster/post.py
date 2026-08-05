import json
import os
import sys
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
OWNER_ID = "5911159063"  # Thiha Tun's Telegram ID

CONTENT_FILE = "content.json"
STATE_FILE = "post_state.json"
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def send_message(chat_id, text):
    """Send a text message."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(url, json=payload, timeout=30)
    return resp


def send_photo(chat_id, image_path, caption):
    """Send a photo with caption."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as photo:
        resp = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": photo},
            timeout=60,
        )
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
        print("Content အားလုံး တင်ပြီးသွားပါပြီ။ Day 1 ကနေ ပြန်စပါမယ်။")

    post = content[idx]
    caption = post["caption"]
    image_file = post.get("image")

    # Ensure @ThihaDigitalBot is in every post
    if "@ThihaDigitalBot" not in caption:
        caption += "\n\n🤖 မှာယူရန်: @ThihaDigitalBot"

    # Send to channel
    success = False
    if image_file:
        image_path = os.path.join(IMAGES_DIR, image_file)
        if os.path.exists(image_path):
            resp = send_photo(CHAT_ID, image_path, caption)
            if resp.status_code == 200 and resp.json().get("ok"):
                success = True
            else:
                print(f"Photo send failed: {resp.status_code} {resp.text}")
                # Fallback to text-only
                resp = send_message(CHAT_ID, caption)
                if resp.status_code == 200 and resp.json().get("ok"):
                    success = True
        else:
            print(f"Image not found: {image_path}, sending text only")
            resp = send_message(CHAT_ID, caption)
            if resp.status_code == 200 and resp.json().get("ok"):
                success = True
    else:
        resp = send_message(CHAT_ID, caption)
        if resp.status_code == 200 and resp.json().get("ok"):
            success = True

    if not success:
        error_msg = f"❌ Evening Promo Post (Day {idx + 1}/{len(content)}) fail ဖြစ်ပါတယ်"
        print(error_msg)
        send_message(OWNER_ID, error_msg)
        sys.exit(1)

    day_num = post.get("day", idx + 1)
    print(f"Day {day_num} evening promo post တင်ပြီးပါပြီ။")

    # Notify owner about successful post
    send_message(
        OWNER_ID,
        f"📢 Evening Promo Post (Day {idx + 1}/{len(content)}) တင်ပြီးပါပြီ ✅"
    )

    # Move to next day
    state["last_index"] = idx + 1
    save_json(STATE_FILE, state)


if __name__ == "__main__":
    main()
