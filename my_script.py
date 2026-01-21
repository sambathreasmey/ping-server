import requests
import calendar
import os
import datetime
import zoneinfo
from generate import create_card

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SEND_CHAT_ID = os.getenv("SEND_CHAT_ID")
STATE_FILE = "last_price.txt"

def get_last_price():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return "0"

def save_current_price(price):
    with open(STATE_FILE, "w") as f:
        f.write(str(price))

def is_work_period(dt):
    if dt.weekday() > 4: return False
    return 8 <= dt.hour < 15

def main():
    tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
    today = datetime.datetime.now(tz)
    
    if not is_work_period(today):
        print("💤 Market is closed.")
        return

    abc_tracking = get_last_price()
    url = "https://csx.com.kh/api/v1/website/market-data/stock/prices"
    
    # Date Logic
    to_date = today.strftime("%Y%m%d")
    from_date = (today - datetime.timedelta(days=30)).strftime("%Y%m%d")

    payload = {
        "fromDate": from_date,
        "toDate": to_date,
        "symbol": "KH1000100003",
        "tradingMethod": "all",
        "board": "main"
    }

    try:
        response = requests.post(url, params={"lang": "en"}, json=payload, timeout=30)
        data = response.json()
        price_data = data['data']['todayPrice']
        
        new_price = str(price_data['currentPrice'])
        change = price_data['change']
        changePercent = price_data['changePercent']
        upDown = price_data['changeUpDown']

        if new_price != abc_tracking:
            print(f"✅ Price Changed: {new_price}")
            img_path = create_card(upDown, new_price, f"{changePercent}%", change)
            changeUpDown = ""
            # Send to Telegram
            if changeUpDown == "up":
                up_down_equal = "🔺ឡើង"
            elif changeUpDown == "down":
                up_down_equal = "🔻ចុះ"
            else:
                up_down_equal = "▫️ស្មើរ"
            caption = f"<b>ABC {new_price} រៀល</b> {up_down_equal} {change} | <b>{changePercent}%</b>"
            with open(img_path, "rb") as img:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                              data={"chat_id": SEND_CHAT_ID, "caption": caption, "parse_mode": "HTML"},
                              files={"photo": img})
            
            save_current_price(new_price)
        else:
            print("No price change.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
