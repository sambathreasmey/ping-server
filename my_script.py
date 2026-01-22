import requests
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

def get_khmer_now():
    tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
    now = datetime.datetime.now(tz)
    
    # Khmer Mappings
    months_kh = {
        "Jan": "មករា", "Feb": "កុម្ភៈ", "Mar": "មីនា", "Apr": "មេសា",
        "May": "ឧសភា", "Jun": "មិថុនា", "Jul": "កក្កដា", "Aug": "សីហា",
        "Sep": "កញ្ញា", "Oct": "តុលា", "Nov": "វិច្ឆិកា", "Dec": "ធ្នូ"
    }
    am_pm_kh = {"AM": "ព្រឹក", "PM": "ល្ងាច"}

    # Get standard parts
    year = now.strftime("%Y")
    month = months_kh[now.strftime("%b")]
    day = now.strftime("%d")
    time_str = now.strftime("%I:%M:%S")
    period = am_pm_kh[now.strftime("%p")]

    # Format: 2026 មករា 22 | 09:27:54 ព្រឹក
    return f"{year} {month} {day} | {time_str} {period}"

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
            up_down_equal = ""
            # Send to Telegram
            if upDown == "up":
                up_down_equal = "🔺ឡើង"
            elif upDown == "down":
                up_down_equal = "🔻ចុះ"
            else:
                up_down_equal = "▫️ស្មើរ"
            caption = f"<b>ABC {new_price} រៀល</b> {up_down_equal} {change} | <b>{changePercent}%</b>"
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
            
            save_current_price(new_price)
            # Log results to file
            with open("log.txt", "a") as f:
                f.write(f"{get_khmer_now()} | Status: {up_down_equal} | Price: {new_price} | Change: {change} | ChangePercent: {changePercent}\n")
        else:
            print("No price change.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
