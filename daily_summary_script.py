import time
import os
import requests

from generate import create_card_v2

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SEND_CHAT_ID = os.getenv("SEND_CHAT_ID")

def main():
    try:
        push_telegram()
    except Exception as e:
        print(f"Error: {e}")

def push_telegram():
    issueName = "PPWSA"
    changeUpDown = "up"
    currentPrice = "11,020"
    percentChange = "0.18"
    change = 20
    issueSummary = "Upper (11,020) +4.36% | Lower (10,700) -2.73%"
    
    img_path = create_card_v2(issueName, changeUpDown, currentPrice, f"{percentChange}%", change, issueSummary)
    up_down_equal = ""
    # Send to Telegram
    if changeUpDown == "up":
        up_down_equal = "🟢ឡើង"
    elif changeUpDown == "down":
        up_down_equal = "🔴ចុះ"
    else:
        up_down_equal = "⚫️ស្មើរ"
    caption = f"<b>{issueName} {currentPrice} រៀល</b> {up_down_equal} {change} | <b>{percentChange}%</b>"
    try:
        with open(img_path, "rb") as img:
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                data={"chat_id": SEND_CHAT_ID, "caption": caption, "parse_mode": "HTML"},
                files={"photo": img}
            )
            print(f"Telegram response: {response.status_code}")
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)
            print(f"🗑️ Deleted local file: {img_path}")

if __name__ == "__main__":
    main()
